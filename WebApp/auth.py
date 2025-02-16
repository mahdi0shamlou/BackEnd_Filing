from flask import request, Blueprint, jsonify
import redis
import random
import datetime
import re
#-------------jwt tokens
from flask_jwt_extended import create_access_token
#-------------
#------------- models
from models import users as Users
from models import db
#---------------
#--------------- code sender
from kavenegar import *
#----------------

auth_bp = Blueprint('auth', __name__)

def is_valid_iranian_phone(phone):
    pattern = r'^0\d{10}$'
    return re.match(pattern, phone) is not None

def codesender(phone):
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    # تولید کد 4 رقمی
    code = random.randint(1000, 9999)

    # ذخیره کد در Redis با کلید شماره تلفن
    redis_client.set(phone, code, ex=300)  # کد به مدت 5 دقیقه (300 ثانیه) معتبر است

    api = KavenegarAPI('2B393856314B72454C624855696979686A4F574D416A766B366444674A364149554E6A69393452747965513D')
    params = {
        'receptor': phone,
        'template': 'verify',
        'token': code,
        'type': 'sms'
    }
    response = api.verify_lookup(params=params)
    return response

def code_cheker(phone, code):
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    # دریافت کد ذخیره شده از Redis
    stored_code = redis_client.get(phone)
    # بررسی مطابقت کد وارد شده و کد ذخیره شده
    return stored_code == code

@auth_bp.route('/Login', methods=['POST'])
def login():
    data = request.form
    phone = data.get('phone')

    if is_valid_iranian_phone(phone):
        user = Users.query.filter_by(phone=phone).first()
        if user:
            codesender(phone)
            return jsonify({"Text": "اس ام اس برای شما ارسال شد"}), 200
        else:
            user = Users(username="user_" + str(datetime.datetime.now().timestamp()),  # نام کاربری پیش‌فرض
                         password="defaultpassword",  # کلمه عبور پیش‌فرض، باید تغییر کند
                         name="Default Name",  # نام پیش‌فرض
                         phone=phone,
                         email="default@example.com")  # ایمیل پیش‌فرض، باید تغییر کند
            db.session.add(user)
            db.session.commit()
            codesender(phone)
            return jsonify({"Text": "اس ام اس برای شما ارسال شد"}), 200

    else:
        return jsonify({"error": "شماره تلفن وارد شده معتبر نیست ."}), 400

@auth_bp.route('/Login/Code', methods=['POST'])
def code_checker_login():
    data = request.form
    phone = data.get('phone')
    code = data.get('code')
    if is_valid_iranian_phone(phone):
        if not code:
            return jsonify({"error": "کد احراز را وارد کنید ."}), 400

        user = Users.query.filter_by(phone=phone).first()

        if user:
            response_checker = code_cheker(phone, code)
            if response_checker:

                expires = datetime.timedelta(days=30)
                access_token = create_access_token(identity={"phone": user.phone}, expires_delta=expires)
                user.jwt_token = access_token
                db.session.commit()
                return jsonify({"Text": "ورود شما موفقیت آمیز بود !", "access_token": access_token}), 200
            else:
                return jsonify({"Text": "کد وارد شده درست نبود !"}), 400

        else:
            return jsonify({"Text": "کاربر ثبت نام نشده است !"}), 400
    else:
        return jsonify({"error": "شماره تلفن وارد شده معتبر نیست ."}), 400