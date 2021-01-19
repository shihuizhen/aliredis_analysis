from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
# redis
from aliyunsdkr_kvstore.request.v20150101.DescribeInstancesRequest import DescribeInstancesRequest
# DAS
from aliyunsdkdas.request.v20200116.CreateCacheAnalysisJobRequest import CreateCacheAnalysisJobRequest
# 获取查询分析详情根据jobid
from aliyunsdkdas.request.v20200116.DescribeCacheAnalysisJobRequest import DescribeCacheAnalysisJobRequest
# 获取查询分析列表 根据时间范围
from aliyunsdkdas.request.v20200116.DescribeCacheAnalysisJobsRequest import DescribeCacheAnalysisJobsRequest
from settings import aliyun_client
import json
from datetime import date


class RequestJobError(Exception):
    pass

class CreateJobError(Exception):
    pass

class AliyunRedis:
    def __init__(self):
        self.client = AcsClient(*aliyun_client.values())
        self.dasclient = AcsClient(
            aliyun_client["accessKeyId"], aliyun_client["accessSecret"], "cn-shanghai")

    def get_all_instances_info(self):
        # 获取所有节点最多循环100次
        page_number = 1
        page_size = 100  # 100 * page_size 需要小于总实例数
        all_instances_info = list()
        for i in range(1, 100):
            request = DescribeInstancesRequest()
            request.set_accept_format('json')
            request.set_PageNumber(page_number)
            request.set_PageSize(page_size)
            response = self.client.do_action_with_exception(request)
            response_dict = json.loads(response)
            # if response_dict["Success"] == False:
            #     raise Exception("接口请求失败. response:{0}".format(response_dict))
        
            all_instances_info.extend(
                response_dict["Instances"]["KVStoreInstance"])
            if int(response_dict["PageNumber"])*int(response_dict["PageSize"]) >= int(response_dict["TotalCount"]):
                break
            elif len(response_dict["Instances"]["KVStoreInstance"]) == 0:
                break
            else:
                page_number = page_number + 1
        all_instances_info = self.format_instances_info(all_instances_info)
        return all_instances_info

    def format_instances_info(self, instances_info_response):
        formated_instances_info = [
            {
                "instance_id": x["InstanceId"],
                "instance_name": x["InstanceName"],
                "region_id": x["RegionId"],
                "instance_type": x["ArchitectureType"]
            }
            for x in instances_info_response
        ]

        return formated_instances_info

# 留存jobid
    def create_cache_analysisjob(self, instance_id):

        request = CreateCacheAnalysisJobRequest()
        request.set_InstanceId(instance_id)
        response = self.dasclient.do_action_with_exception(request)
        response_dict = json.loads(response)
        
        if response_dict["Success"] == False:
            raise CreateJobError("创建job失败! instance_id:{0}".format(instance_id))

        return self.format_analysisjob(response_dict)


    def format_analysisjob(self, analysisjob_response):
        analysisjob_response_data = analysisjob_response["Data"]
        formated_analysisjob_response = {
            "instance_id": analysisjob_response_data["InstanceId"],
            "node_id": analysisjob_response_data["NodeId"],
            "task_state": analysisjob_response_data["TaskState"],
            "job_id": analysisjob_response_data["JobId"],
            "success": analysisjob_response["Success"]
        }

        return formated_analysisjob_response

    def get_analysisjob_info(self, instance_id, job_id):
        request = DescribeCacheAnalysisJobRequest()
        request.set_InstanceId(instance_id)
        request.set_JobId(job_id)
        response = self.dasclient.do_action_with_exception(request)
        response_dict = json.loads(response)
        if response_dict["Success"] == False:
            raise RequestJobError("接口请求失败. instance_id:{0}, job_id:{1}, response:{2}".format(instance_id, job_id, response_dict))
        
        job_data = dict()
        if response_dict["Data"]["TaskState"] == "FINISHED":
            job_data = {
                "bigkeys": response_dict["Data"]["BigKeys"],
                "keyprefixes": response_dict["Data"]["KeyPrefixes"]
            }
        else:
            job_data = None
        if response_dict["Data"]["TaskState"] == "FAILED":
            raise Exception("作业分析失败. instance_id:{0}, job_id:{1}".format(instance_id, job_id))
        formated_analysisjob_info = self.format_analysisjob(response_dict)

        return formated_analysisjob_info, job_data


