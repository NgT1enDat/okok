from mongo_connect import mongo_create
from bson.objectid import ObjectId
import requests
import time
import bcrypt
from slugify import slugify
from datetime import datetime
db = mongo_create()
account = db.account
hq = db.hq
register = db.register

client_id = '620620a3643d404e347281f3'
campaign_id = '620626956d0ccc5e728c21cf'


def getNOW():
    return datetime.now().timestamp()


s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'


def remove_accents(input_str):
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s


def create_account(name, phone, email, password):
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    name = remove_accents(name)
    print(name)
    slug = slugify(name)
    print(slug)
    account_item = account.insert_one({
        'name': name,
        'phone': phone,
        'email': email,
        'password': password,
        'first_login': True,
        'is_verify': False,
        'slug': slug,
        'when': time.time()
    })
    return account_item


def find_account_by_id(account_id):
    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)
    return account.find_one({'_id': account_id})


def find_account_by_mail(email):
    return account.find_one({'email': email})


def find_account_by_phone(phone):
    return account.find_one({'phone': phone})


def check_account_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)


def find_last_hq(account_id):
    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)
    hq_cursor = hq.find({'account_id': account_id}).sort('when', -1).limit(1)
    return [hq_item for hq_item in hq_cursor]