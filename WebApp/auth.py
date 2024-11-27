from flask import request, Blueprint, jsonify
import redis
import random
import datetime
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


def codesender(phone):
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    # تولید کد 4 رقمی
    code = random.randint(1000, 9999)

    # ذخیره کد در Redis با کلید شماره تلفن
    redis_client.set(phone, code, ex=300)  # کد به مدت 5 دقیقه (300 ثانیه) معتبر است

    api = KavenegarAPI('66765175557259455153354358533233384E4A6B75535141797250697644616A69637538763243726535513D')
    params = {
        'receptor': phone,
        'template': 'otp',
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
    #phone = request.json.get('phone')
    if not phone:
        return jsonify({"error": "شماره تلفن را وارد کنید ."}), 400

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

@auth_bp.route('/Login/Code', methods=['POST'])
def code_checker_login():
    data = request.form
    phone = data.get('phone')
    code = data.get('code')

    if not phone:
        return jsonify({"error": "شماره تلفن را وارد کنید ."}), 400
    if not code:
        return jsonify({"error": "کد احراز را وارد کنید ."}), 400

    user = Users.query.filter_by(phone=phone).first()

    if user:
        response_checker = code_cheker(phone, code)
        if response_checker:
            access_token = create_access_token(identity={"phone": user.phone})
            return jsonify({"Text": "ورود شما موفقیت آمیز بود !", "access_token": access_token}), 200
        else:
            return jsonify({"Text": "کد وارد شده درست نبود !"}), 400

    else:
        return jsonify({"Text": "کاربر ثبت نام نشده است !"}), 400