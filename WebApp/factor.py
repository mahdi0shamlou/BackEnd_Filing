from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import db
from models import Factor

# ---------------
# def price
# ---------------
def Get_price(data):
    factor_type = data.get('type')
    number = data.get('number', 1)
    classifications = data.get('classifications', [])
    time_delta = data.get('time_delta', 30)
    
    price = 1000
    return price

factors_bp = Blueprint('factor', __name__)

@factors_bp.route('/Factors/List', methods=['GET'])
@jwt_required()
def get_factors():
    # دریافت اطلاعات کاربر فعلی از توکن JWT
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # پیدا کردن کاربر در دیتابیس
    user = Users.query.filter_by(phone=user_phone).first()

    try:
        # پیدا کردن فاکتورهای مربوط به کاربر فعلی
        factors = Factor.query.filter_by(user_id=user.id).all()

        # تبدیل فاکتورها به فرمت جیسون
        factors_list = [{
            "id": factor.id,
            "status": factor.status,
            "type": factor.type,
            "number": factor.number,
            "price": factor.price,
            "created_at": factor.created_at.isoformat(),
            "expired_at": factor.expired_at.isoformat(),
            "updated_at": factor.updated_at.isoformat() if factor.updated_at else None
        } for factor in factors]

        return jsonify({"factors": factors_list}), 200

    except Exception as e:
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در دریافت فاکتورها"}), 500

@factors_bp.route('/Factors/New', methods=['POST'])
@jwt_required()
def create_factor():
    # دریافت اطلاعات کاربر فعلی از توکن JWT
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # پیدا کردن کاربر در دیتابیس
    user = Users.query.filter_by(phone=user_phone).first()

    # دریافت داده‌های ارسالی
    data = request.get_json()

    if not data:
        return jsonify({"message": "داده‌ای دریافت نشد!"}), 400

    try:
        # واکشی و اعتبارسنجی اطلاعات فاکتور
        factor_type = data.get('type')
        number = data.get('number', 1)
        time_delta = data.get('time_delta', 30)  # اگر داده‌ای وجود نداشته باشد، پیش‌فرض 30 خواهد بود
        if time_delta not in [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]:
            return jsonify({"message": "خطا در ایجاد فاکتور تعداد روز ها باید به ماه باشد"}), 500
        # زمان فعلی
        now = datetime.now()
        # محاسبه تاریخ جدید با اضافه کردن time_delta به زمان فعلی
        new_date = now + timedelta(days=time_delta)

        # اعتبارسنجی مقدماتی
        if not all([factor_type]):
            return jsonify({"message": "تمام فیلدهای مورد نظر را وارد کنید!"}), 400

        # ایجاد فاکتور جدید
        new_factor = Factor(
            user_id=user.id,
            status=0,
            type=factor_type,
            number=number,
            price=Get_price(data),
            expired_at=new_date
        )

        db.session.add(new_factor)
        db.session.commit()

        return jsonify({
            "message": "فاکتور با موفقیت ایجاد شد",
            "factor": {
                "id": new_factor.id,
                "status": new_factor.status,
                "type": new_factor.type,
                "number": new_factor.number,
                "price": new_factor.price,
                "created_at": new_factor.created_at.isoformat(),
                "expired_at": new_factor.expired_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در ایجاد فاکتور"}), 500

@factors_bp.route('/Factors/Delete/<int:factor_id>', methods=['DELETE'])
@jwt_required()
def delete_factor(factor_id):
    # دریافت اطلاعات کاربر فعلی از توکن JWT
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # پیدا کردن کاربر در دیتابیس
    user = Users.query.filter_by(phone=user_phone).first()

    try:
        # پیدا کردن فاکتور بر اساس ID و کاربر جاری
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()

        if not factor:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد"}), 404

        # بررسی وضعیت فاکتور
        if factor.status not in [0, 2]:
            return jsonify({"message": "فقط فاکتورهایی با وضعیت عدم پرداخت یا مهلت پرداخت تمام شده قابل حذف هستند"}), 400

        # حذف فاکتور
        db.session.delete(factor)
        db.session.commit()

        return jsonify({"message": "فاکتور با موفقیت حذف شد"}), 200

    except Exception as e:
        db.session.rollback()
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در حذف فاکتور"}), 500

#--------------------------------------
# Routes Of Prices
#--------------------------------------

@factors_bp.route('/Factors/Price', methods=['GET'])
@jwt_required()
def get_factors_price():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "داده‌ای دریافت نشد!"}), 400

        price = Get_price(data)
        return jsonify({"Prices": price}), 200

    except Exception as e:
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در دریافت قیمت"}), 500
