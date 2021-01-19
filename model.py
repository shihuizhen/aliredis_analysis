from typing import Text
from aliyunsdkcore.endpoint import default_endpoint_resolver
from sqlalchemy import engine
from sqlalchemy.sql.sqltypes import DATETIME, DATE
from settings import cmdb

import sqlalchemy
from sqlalchemy.sql import func, text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from session import get_db


Base = declarative_base()

# model


class Instances_Info(Base):
    # 表的名字:
    __tablename__ = 'instances_info'

    # 表的结构:
    instance_id = Column(String(64), primary_key=True)
    instance_name = Column(String(64), index=True, nullable=False)
    region_id = Column(String(16), nullable=False)
    instance_type = Column(String(16), nullable=False)
    isdel = Column(Integer, default=0, nullable=False)
    # server_onupate, onupdate, server_default, default. 配置server 则在建表语句中生成自动时间戳
    # update_time = Column(DATETIME, server_onupdate=func.now())
    update_time = Column(DATETIME, nullable=False, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))



class Analysis_Job(Base):
    __tablename__ = 'analysis_job'

    job_id = Column(String(64), primary_key=True)
    instance_id = Column(String(64), nullable=False)
    node_id = Column(String(64), nullable=False)
    task_state = Column(String(50), index=True)
    success = Column(String(16), nullable=False)
    create_day = Column(DATE, nullable=False)
    save_data_status = Column(
        Integer, nullable=False, default=0, comment="0:数据未保存,1:数据保存中,2:数据已经保存,3:数据保存失败")

    Index('instance_id', 'create_day')
    Index('create_day', 'task_state')

class Alarm_log(Base):
    __tablename__ = 'alarm_log'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    instance_id = Column(String(64), index=True, nullable=False)
    instance_name = Column(String(64), index=True, nullable=False)
    message = Column(String(3000), nullable=False)
    sended = Column(Integer, default=0, nullable=False)
    create_time = Column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DATETIME, nullable=False, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    Index('create_time', 'sended')
    

class CRUD_Instances_Info:

    @staticmethod
    def in_update_notin_insert(session, instance_info_dict: dict):
        # one() 如果无返回报异常sqlalchemy.orm.exc.NoResultFound: No row was found for one(). one_or_none()
        row_info = session.query(Instances_Info).filter(
            Instances_Info.instance_id == instance_info_dict["instance_id"]).one_or_none()
        if row_info:
            session.query(Instances_Info).filter(
                Instances_Info.instance_id == instance_info_dict["instance_id"]).update(instance_info_dict)
            session.commit()
        else:
            row_info = Instances_Info(**instance_info_dict)
            session.add(row_info)
            session.commit()
        return 0

    @staticmethod
    def get_all_instances(session):
        rows = session.query(Instances_Info.instance_id).filter(
            Instances_Info.isdel == 0).all()
        return rows

    @staticmethod
    def get_instance(session, instance_id):
        row = session.query(Instances_Info.instance_id, Instances_Info.instance_name,Instances_Info.isdel).filter(
            Instances_Info.instance_id == instance_id).first()
        return row
    
    @staticmethod
    def disable_instance(session, instance_id):
        res = session.query(Instances_Info).filter(Instances_Info.instance_id == instance_id).update({"isdel":1})
        session.commit()
        return res

    @staticmethod
    def enable_instance(session, instance_id):
        res = session.query(Instances_Info).filter(Instances_Info.instance_id == instance_id).update({"isdel":0})
        session.commit()
        return res

        

class CRUD_Analysis_Job:

    @staticmethod
    def in_update_notin_insert(session, analysis_job_info: dict):
        # one() 如果无返回报异常sqlalchemy.orm.exc.NoResultFound: No row was found for one(). one_or_none()
        row_info = session.query(Analysis_Job).filter(
            Analysis_Job.job_id == analysis_job_info["job_id"]).one_or_none()
        if row_info:
            session.query(Analysis_Job).filter(
                Analysis_Job.job_id == analysis_job_info["job_id"]).update(analysis_job_info)
            session.commit()
        else:
            row_info = Analysis_Job(
                **analysis_job_info, create_day=date.today())
            session.add(row_info)
            session.commit()
        return 0

    @staticmethod
    def get_currentday_not_finnish_job(session,day):
        today = day
        rows = session.query(Analysis_Job).filter(Analysis_Job.create_day == today).filter(
            Analysis_Job.task_state.in_(['BACKUP', 'ANALYZING', 'USER_ENABLE'])).filter(Analysis_Job.save_data_status == 0).all()
        # session.commit()
        return rows

    @staticmethod
    def get_currentday_not_savedata_job(session):
        today = date.today()
        rows = session.query(Analysis_Job).filter(Analysis_Job.create_day == today).filter(
            Analysis_Job.task_state.in_(['FINISHED'])).filter(Analysis_Job.save_data_status == 0).all()
        # session.commit() # 返回需要绑定session 如果commit 返回结果在session 回收后值不能访问
        return rows

    @staticmethod
    def update_job_save_data_status(session, job_id, savedatastatus):
        res = session.query(Analysis_Job).filter(
            Analysis_Job.job_id == job_id).update({"save_data_status": savedatastatus})
        session.commit()
        return res
    
    @staticmethod
    def disable_job(session, job_id):
        res = session.query(Analysis_Job).filter(
            Analysis_Job.job_id == job_id).update({"task_state": "USER_DISABLE"})
        session.commit()
        return res
    
    @staticmethod
    def enable_job(session, job_id):
        res = session.query(Analysis_Job).filter(
            Analysis_Job.job_id == job_id).update({"task_state": "USER_ENABLE"})
        session.commit()
        return res


class CRUD_Alarm_Log:
    
    @staticmethod
    def insert(session, alarm_log_dict: dict):
        row_info = Alarm_log(
            **alarm_log_dict)
        session.add(row_info)
        session.commit()
        return row_info
    
    @staticmethod
    def get_not_sended_log(session, begin_time):
        rows = session.query(Alarm_log).filter(Alarm_log.create_time >= begin_time).filter(Alarm_log.sended == 0).all()
        
        return rows
    
    @staticmethod
    def set_log_is_sended(session, log_id):
        res = session.query(Alarm_log).filter(Alarm_log.log_id == log_id).update({"sended":1})
        session.commit()
        return res
    
# if __name__ == "__main__":
#     engine = create_engine(
#         "mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(**cmdb), max_overflow=5)
    # 初始化表
    # Base.metadata.create_all(engine)
    # 初始化所有未创建建
    # Base.metadata.create_all(engine, Base.metadata.tables.values(),checkfirst=True)
    # 初始化指定表
    # table_objects = [Base.metadata.tables["alarm_log"]]

    # Base.metadata.create_all(engine, tables=table_objects,checkfirst=True)


