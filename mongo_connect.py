from pymongo import MongoClient
import setting
from collections import OrderedDict
import sys


def mongo_create():
    mongodb = MongoClient(
        setting.MONGODB_HOST,
        setting.MONGODB_PORT,
        # document_class=OrderedDict,
        maxPoolSize=200,
        serverSelectionTimeoutMS=90000)

    mydb = mongodb[setting.MONGODB_NAME]
    if 'local' not in sys.argv:
        mydb.authenticate(setting.MONGODB_USER,
                          setting.MONGODB_PASSWORD)
    return mydb
