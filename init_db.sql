-- 初始化数据库

CREATE DATABASE `aliyun_cmdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

-- 初始化表

CREATE TABLE `alarm_log` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `instance_id` varchar(64) NOT NULL,
  `instance_name` varchar(64) NOT NULL,
  `message` varchar(3000) NOT NULL,
  `sended` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `ix_alarm_log_instance_name` (`instance_name`),
  KEY `ix_alarm_log_instance_id` (`instance_id`),
  KEY `ix_alarm_log_ctime_sended` (`create_time`, `sended`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `analysis_job` (
  `job_id` varchar(64) NOT NULL,
  `instance_id` varchar(64) NOT NULL,
  `node_id` varchar(64) NOT NULL,
  `task_state` varchar(50) DEFAULT NULL,
  `success` varchar(16) NOT NULL,
  `create_day` date NOT NULL,
  `save_data_status` int(11) NOT NULL COMMENT '0:数据未保存,1:数据保存中,2:数据已经保存,3:数据保存失败',
  PRIMARY KEY (`job_id`),
  KEY `ix_analysis_job_task_state` (`task_state`),
  KEY `idx_cday_tsta`(`create_day`, `task_state`),
  KEY `idx_iid_cday`(`instance_id`, `create_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `instances_info` (
  `instance_id` varchar(64) NOT NULL,
  `instance_name` varchar(64) NOT NULL,
  `region_id` varchar(16) NOT NULL,
  `instance_type` varchar(16) NOT NULL,
  `isdel` int(11) NOT NULL,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`instance_id`),
  KEY `ix_instances_info_instance_name` (`instance_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;