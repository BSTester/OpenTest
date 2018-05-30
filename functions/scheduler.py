import time
from modules.setting import SettingModule
from functions.test_runner import TestRunner
from tornado import gen
from tornado.log import app_log as log


class JobsMonitor(object):
    def __init__(self):
        self.setting = SettingModule()

    # 监控任务状态
    @gen.coroutine
    def jobs_status(self):
        try:
            s_setting, total = yield self.setting.get_settings_list(s_type='job', status=0, pj_status=1, limit=None)
            for row in s_setting:
                if int(time.time()) > int(float(row.name)):
                    yield self.setting.edit_setting(sid=row.id, status=1)
        except Exception as e:
            log.warning(e)

    # 执行定时任务
    @gen.coroutine
    def run_jobs(self):
        try:
            s_setting, total = yield self.setting.get_settings_list(s_type='job', status=1, pj_status=1, limit=None)
            for row in s_setting:
                test = TestRunner(row.project_id, row.id)
                test.run_job()
        except Exception as e:
            log.warning(e)


def job_monitor():
    job = JobsMonitor()
    job.jobs_status()
    job.run_jobs()
