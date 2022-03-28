from datetime import datetime, timedelta
from tasks import celery
from model import User
from flask_login import LoginManager, login_user, login_required, current_user
from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    sessions,
    url_for,
    send_file,
    abort,
)
from flask_httpauth import HTTPDigestAuth
import sys
import api
import pymongo
from flask_paginate import Pagination
import random
import json
import setting
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key here'
auth = HTTPDigestAuth()


users = {
    "its": "its",
}


ITEMS_PER_PAGE = 2


@app.template_filter('convert_utc_7')
def convert_utc_7(value):
    try:
        if len(str(value)) == 13:
            value = value / 1000
        return datetime.fromtimestamp(int(value)+25200).strftime("%Y/%m/%d %H:%M:%S")
    except:
        return ''


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    user = api.find_account_by_id(userid)
    if user:
        g.user = user
        hq = api.find_last_hq(user.get('_id'))
        if len(hq) > 0:
            hq = hq[0]
            g.hq = hq
    else:
        pass
    return User(userid)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/signin')


@app.route('/')
def index():
    return render_template('signin.html')


@app.route('/signin', methods=["POST","GET"])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = api.find_account_by_mail(email)
        if user and User.validate_login(user['password'], password):
            user_obj = User(str(user['_id']))
            g.user = user
            login_user(user_obj)
            return json.dumps({'result': True})
        return json.dumps({'result': False})
    return render_template('signin.html')


@app.route('/signup', methods=["POST","GET"])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        if not name or len(name) == 0:
            return json.dumps({
                'result': False,
                'error': 'Tên không được để trống'
            })
        if not phone:
            return json.dumps({
                'result': False,
                'error': 'Số điện thoại không được để trống'
            })
        if not email:
            return json.dumps({
                'result': False,
                'error': 'Email không được để trống'
            })
        if not password:
            return json.dumps({
                'result': False,
                'error': 'Vui lòng điền mật khẩu'
            })
        email_check = api.find_account_by_mail(email)
        if email_check:
            return json.dumps({
                 'result':
                False,
                'error':
                'Email đã đăng ký tài khoản khác, vui lòng đăng nhập hoặc sử dụng email khác'
            })
        phone_check = api.find_account_by_phone(phone)
        if phone_check:
            return json.dumps({
                'result':
                False,
                'error':
                'Số điện thoại đã đăng ký tài khoản khác, vui lòng đăng nhập hoặc sử dụng email khác'
            })
        api.create_account(name, phone, email, password)
        return json.dumps({'result': True})
    return render_template('signup.html')


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        email = request.form.get("email")
        exist_email_register = api.register.find_one({'email': email})
        if exist_email_register:
            return json.dumps({'code': 0, 'msg': 'Email đã tồn tại trong hệ thống.<br/>Vui lòng chọn số khác'})
        phone = request.form.get("phone")
        exist_phone_register = api.register.find_one({'phone': phone})
        if exist_phone_register:
            return json.dumps({'code': 0, 'msg': 'Số điện thoại đã tồn tại trong hệ thống.<br/>Vui lòng chọn số khác'})
        if len(phone) not in [10, 11]:
            return json.dumps({'code': 0, 'msg': 'Số điện thoại không hợp lệ'})
        gender = request.form.get("gender")
        dob = request.form.get("dob")
        address = request.form.get("address")
        add_user = {
            "email": email,
            "phone": phone,
            "gender": gender,
            'dob': dob,
            "address": address,
        }
        api.register.insert_one(add_user)

    register_list = api.register.find()

    return render_template('register.html', register_list=register_list, provinces=setting.list_provinces)


@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    filter = {

    }
    count_logs = api.register.count_documents(filter)
    page = int(request.args.get('page', 1))
    pagination = Pagination(
        page=page,
        total=count_logs,
        per_page=ITEMS_PER_PAGE,
        css_framework='bootstrap3')
    recs = api.register.find(filter).sort("created_at", pymongo.DESCENDING).skip(
        ITEMS_PER_PAGE * (page - 1)).limit(ITEMS_PER_PAGE)
    return render_template('manage.html', register_list=recs, pagination=pagination)


if __name__ == '__main__':
    if 'local' in sys.argv:
        app.run(host="127.0.0.1", port=9500, debug=True)
    else:
        app.run(host="0.0.0.0", port=9500)
