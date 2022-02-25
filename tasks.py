from datetime import timedelta, datetime
from celery import Celery
from redisbeat.scheduler import RedisScheduler
from celery.schedules import crontab
import setting
from bson.objectid import ObjectId
import json
from pymongo import MongoClient
import api

CELERY_BROKER_URL = setting.CELERY_URL
CELERY_RESULT_BACKEND = setting.CELERY_URL
celery = Celery('tasks', backend=CELERY_RESULT_BACKEND,
                broker=CELERY_BROKER_URL, timezone='Asia/Ho_Chi_Minh')
celery.conf.update(CELERY_REDIS_SCHEDULER_URL=CELERY_BROKER_URL)

celery.conf.beat_schedule = {
    # 'init': {
    #     'task': 'tasks.init',
    #     'schedule': timedelta(seconds=5),
    #     'args': (),
    # },
    # 'check_and_remove_task': {
    #     'task': 'tasks.check_and_remove_task',
    #     'schedule': crontab(),
    #     'args': (),
    # },
}


@celery.task(name='makecall', serializer='json')
def makecall(phone):
    api.make_call(phone)
    return 'makecall'


# celery -A tasks flower  --address=127.0.0.1 --port=5567
# celery -A tasks worker -l INFO -P eventlet --autoscale=8,4 --loglevel=INFO
