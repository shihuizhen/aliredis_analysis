import click
from datetime import date, datetime, timedelta
from time import sleep
from click.types import STRING
from click.utils import get_binary_stream

from sqlalchemy.sql import expression
from sqlalchemy.sql.functions import array_agg
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.util.compat import with_metaclass
from alicache import AliyunRedis, RequestJobError, CreateJobError
from model import CRUD_Instances_Info, CRUD_Analysis_Job, CRUD_Alarm_Log
from logger import app_logger
from session import get_db, get_influxdb
from savedata import Redis_BigKeys
from dingpush import dingclient
from alarm import check_keys

try:
    ALIREDIS = AliyunRedis()
except Exception as ex:
    app_logger.error("初始化AliyunRedis类失败, ex:{0}".format(ex), exc_info=True)


def reflush_redis_instances():
    app_logger.info("开始刷新实例!")
    try:
        all_instances_info = ALIREDIS.get_all_instances_info()
    except Exception as ex:
        app_logger.error("获取实例信息失败, ex:{0}".format(ex), exc_info=True)
        raise Exception("获取实例信息失败")
    app_logger.info("刷新实例!完成")

    with get_db() as session:
        for instances_info in all_instances_info:
            app_logger.info(
                "开始更新实例信息,instances_info:{0}".format(instances_info))
            try:
                CRUD_Instances_Info.in_update_notin_insert(
                    session, instances_info)
            except Exception as ex:
                app_logger.error("更新实例信息失败! instances_info:{0}".format(
                    instances_info), exc_info=True)
        app_logger.info("刷新实例完成")

    return 0


def create_analysis_job(instance_id=None):
    instances = []
    if instance_id:
        try:
            job_info = ALIREDIS.create_cache_analysisjob(instance_id)
            # 如果存入数据库失败需要根据日志手工补
            app_logger.info("新job信息:{0}".format(job_info))
            with get_db() as session:
                CRUD_Analysis_Job.in_update_notin_insert(session, job_info)
        except Exception as ex:
            app_logger.error("创建job,跟新job表失败, ID:{0} ex:{1}".format(
                instance_id, ex), exc_info=True)
    else:
        try:
            with get_db() as session:
                instances = CRUD_Instances_Info.get_all_instances(session)
        except Exception as ex:
            app_logger.error("获取实例列表出错", exc_info=True)
            raise Exception("获取实例列表出错")

    if len(instances) == 0:
        app_logger.info("实例id为空值")
        return 0

    for instance in instances:
        try:
            job_info = ALIREDIS.create_cache_analysisjob(instance.instance_id)
            app_logger.info("新job信息:{0}".format(job_info))
            with get_db() as session:
                CRUD_Analysis_Job.in_update_notin_insert(session, job_info)
        except Exception as ex:
            app_logger.error("创建job,跟新job表失败, ID:{0} ex:{1}".format(
                instance.instance_id, ex), exc_info=True)

    return 0


def sync_and_udpate_day_job(day=str(date.today())):
    app_logger.info("开始更新job状态")
    with get_db() as session:
        try:
            jobs = CRUD_Analysis_Job.get_currentday_not_finnish_job(
                session, day)
        except Exception as ex:
            app_logger.error("获取未完成作业列表失败!", exc_info=True)
            raise Exception("获取未完成作业列表失败!")

    if len(jobs) == 0:
        app_logger.info("无未更新job")
        return 0

    for job in jobs:
        try:
            job_info, job_data = ALIREDIS.get_analysisjob_info(
                job.instance_id, job.job_id)
        except RequestJobError as ex:
            app_logger.error("获取job信息失败! iid:{0},jid:{1},ex:{2}".format(
                job.instance_id, job.job_id, ex), exc_info=True)
            with get_db() as session:
                CRUD_Instances_Info.disable_instance(session, job.instance_id)
                CRUD_Analysis_Job.disable_job(session, job.job_id)     
            app_logger.error("因作业接口调用失败,怀疑实例为空实例,已经禁用实例与作业!! iid:{0},jid:{1}".format(
                job.instance_id, job.job_id))
            continue
        except Exception as ex:
            app_logger.error("获取job信息失败! iid:{0},jid:{1},ex:{2}".format(
                job.instance_id, job.job_id, ex), exc_info=True)
            continue

        try:
            with get_db() as session:
                instance = CRUD_Instances_Info.get_instance(
                    session, job.instance_id)
        except Exception as ex:
            app_logger.error("获取实例信息失败! iid:{0},jid:{1},ex:{2}".format(
                job.instance_id, job.job_id, ex), exc_info=True)
            continue

        if len(instance) == 0:
            continue

        try:
            app_logger.info("开始更新job状态, job_info:{0}".format(job_info))
            with get_db() as session:
                CRUD_Analysis_Job.in_update_notin_insert(session, job_info)
        except Exception as ex:
            app_logger.error("更新job状态失败!job_info:{0}".format(
                job_info), exc_info=True)

        # 如果没有完成分析则跳出
        if job_data == None:
            continue

        try:
            app_logger.info(
                "开始更新key信息, job_info:{0}, job_data:{1}".format(job_info, job_data))
            format_response_dict = Redis_BigKeys.format_big_keys_info(
                job_data, day, instance.instance_id, instance.instance_name)

            if format_response_dict["keys_info"]:
                with get_influxdb() as session:
                    Redis_BigKeys.slave_to_influxdb(
                        session, format_response_dict["keys_info"])

                with get_influxdb() as session:
                    Redis_BigKeys.slave_to_influxdb(
                        session, format_response_dict["keyprefixes"])

        except Exception as ex:
            app_logger.error("存入key信息失败! job_info:{0}, day:{1}, iid:{2}, iname:{3}, ex:{4}".format(
                job_info, day, instance.instance_id, instance.instance_name, ex), exc_info=True)
            continue

        try:
            app_logger.info("更新savedata状态,job_info:{0}".format(job_info))
            with get_db() as session:
                CRUD_Analysis_Job.update_job_save_data_status(
                    session, job.job_id, 1)
        except Exception as ex:
            app_logger.error("更新savedata状态失败! jid:{0},ex:{1}".format(
                job.job_id, ex), exc_info=True)
            continue

        try:
            app_logger.info("生成报警信息,jid:{0}, date:{1}".format(
                job.job_id, format_response_dict["keys_info"]))
            alarm_log_dict = check_keys(format_response_dict["keys_info"])
            # 如果没有触发阈值,则不保存报警信息
            if len(alarm_log_dict) == 0:
                continue

            with get_db() as session:
                CRUD_Alarm_Log.insert(session, alarm_log_dict)
        except Exception as ex:
            app_logger.error("保存alarmlog失败, jid:{0},ex:{1}".format(
                job.job_id, ex), exc_info=True)

    return 0


def alarm_big_key(begin_time=datetime.now() - timedelta(hours=12)):
    begin_time_str = begin_time.strftime("%Y-%m-%d %H:%M:%S")
    app_logger.info("开始发送报警")
    title = "大key报警"
    try:
        with get_db() as session:
            alarm_logs = CRUD_Alarm_Log.get_not_sended_log(
                session, begin_time_str)

    except Exception as ex:
        app_logger.error("获取报警信息失败! ex:{0}".format(ex), exc_info=True)
        raise Exception("获取报警信息失败")

    if len(alarm_logs) == 0:
        app_logger.info("无未发送报警")

    for alarm_log in alarm_logs:
        sleep(2)
        try:
            dingclient.sendto_ding(title, alarm_log.message)
        except Exception as ex:
            app_logger.error("发送报警失败! ex:{0}, message:{1}".format(
                ex, alarm_log.message), exc_info=True)
            continue

        try:
            with get_db() as session:
                CRUD_Alarm_Log.set_log_is_sended(session, alarm_log.log_id)
        except Exception as ex:
            app_logger.error("跟新报警消息状态失败! ex:{0}, message:{1}".format(
                ex, alarm_log.message), exc_info=True)
            continue


@click.group()
def cli():
    pass


@cli.command()
@click.option('-i', 'instance_id', required=True, help='实例ID.')
def disable_instance(instance_id):
    """标记实例为不可用"""
    app_logger.info("禁用实例, iid:{0}".format(instance_id))
    try:
        with get_db() as session:
            CRUD_Instances_Info.disable_instance(session, instance_id)
    except Exception as ex:
        app_logger.error("禁用实例失败, iid:{0}, ex:{1}".format(instance_id, ex))
    return 0


@cli.command()
@click.option('-i', 'instance_id', required=True, help='实例ID.')
def enable_instance(instance_id):
    """标记实例为可用"""
    app_logger.info("启用实例, iid:{0}".format(instance_id))
    try:
        with get_db() as session:
            CRUD_Instances_Info.enable_instance(session, instance_id)
    except Exception as ex:
        app_logger.error("启用实例失败, iid:{0}, ex:{1}".format(instance_id, ex))
    return 0


@cli.command()
@click.option('-j', 'job_id', required=True, help='作业ID.')
def disable_job(job_id):
    """标记job为不可用"""
    app_logger.info("禁用job, jid:{0}".format(job_id))
    try:
        with get_db() as session:
            CRUD_Analysis_Job.disable_job(session, job_id)
    except Exception as ex:
        app_logger.error("禁用job失败, iid:{0}, ex:{1}".format(job_id, ex))
    return 0


@cli.command()
@click.option('-j', 'job_id', required=True, help='作业ID.')
def enable_job(job_id):
    """标记job为可用"""
    app_logger.info("启用job, jid:{0}".format(job_id))
    try:
        with get_db() as session:
            CRUD_Analysis_Job.enable_job(session, job_id)
    except Exception as ex:
        app_logger.error("启用job失败, iid:{0}, ex:{1}".format(job_id, ex))

    return 0

@cli.command()
def refresh_instance():
    "刷新实例列表"
    reflush_redis_instances()
    return 0

@cli.command()
@click.option('-i', 'instance_id', required=True, help='实例ID.')
def manual_create_job(instance_id: String):
    """手工创建job,必须指定实例ID"""
    create_analysis_job(instance_id)
    return 0


@cli.command()
@click.option('-f', 'flush_instances', default=False,
              type=click.BOOL, required=True, help='是否刷新实例列表.')
def cron_create_job(flush_instances=False):
    """创建分析作业"""
    if flush_instances:
        reflush_redis_instances()
    create_analysis_job()
    return 0


@cli.command()
@click.option('-d', 'day', type=click.STRING, help='扫描指定天的job.默认为当天')
def cron_save_job_data(day=None):
    """扫描job状态,保存结果,生成报警信息"""
    if day:
        sync_and_udpate_day_job(day)
    else:
        sync_and_udpate_day_job()

    return 0


@cli.command()
@click.option('-t', 'begin_time',
              type=STRING, help='从哪天的报警日志开始发送.')
def alarm(begin_time: str = None):
    """发送报警"""
    if begin_time:
        begin_time = datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
        alarm_big_key(begin_time)
    else:
        alarm_big_key()

    return 0


if __name__ == '__main__':
    cli()

