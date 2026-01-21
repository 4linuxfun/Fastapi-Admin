from time import sleep
from typing import List
from loguru import logger
import rpyc
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

conn = rpyc.connect('localhost', 18861, config={"allow_public_attrs": True, 'allow_pickle': True})
job_id = 'text_print'
# job = conn.root.add_job('scheduler-server:subprocess_with_channel',
#                         args=['12121', 'ipconfig'], id='12121', )

trigger = CronTrigger(minute='*/20', end_date='2023-02-23 14:30:00',kwargs={'command':'netstat -ant'})
job = conn.root.modify_job('1212121', trigger=trigger)
# jobs: List[Job] = conn.root.get_jobs()
# for job in jobs:
#     logger.debug(job.__dir__())
#     cron = {}
#     for field in job.trigger.fields:
#         logger.debug(field)
#         cron[field.name] = str(field)
#     logger.debug(f"{cron['minute']} {cron['hour']} {cron['day']} {cron['month']} {cron['day_of_week']}")

# job = conn.root.get_jobs()
# print(job)
#
# job = conn.root.remove_job('ffb4137ffc9f4bb08b09d1a51b02547b')
