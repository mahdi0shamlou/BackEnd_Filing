from flask import Blueprint, jsonify, request, url_for, redirect, flash
from datetime import datetime, timedelta
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import UserAccess
from models import db
from models import Factor
from models import Classifictions_FOR_Factors
from models import FactorAccess
from models import PER_Classifictions_FOR_Factors, Users_in_Factors_Acsess
#------------------
#---------- zarinpal
from suds.client import Client
# ---------------
# def price
# ---------------

def Get_price(data):
    factor_type = data.get('type')
    number = data.get('number', 1)
    classifications_for_factors = data.get('classifications_for_factors', [])
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
        classifications_for_factors = data.get('classifications_for_factors', [])
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
        for i in classifications_for_factors:
            new_factor_accses = FactorAccess(
                user_id=user.id,
                factor_id=new_factor.id,
                classifictions_for_factors_id=i,
                expired_at=new_date
            )
            db.session.add(new_factor_accses)
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
        factors = Classifictions_FOR_Factors.query.all()
        # تبدیل فاکتورها به فرمت جیسون
        factors_list = [{
            "id": factor.id,
            "price": factor.price,
            "name": factor.name,
            "created_at": factor.created_at.isoformat()
        } for factor in factors]

        return jsonify({"factors": factors_list}), 200

    except Exception as e:
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در دریافت قیمت"}), 500

#--------------------------------------
# Routes Of Pardakhat
#--------------------------------------

@factors_bp.route('/Factors/do/<int:factor_id>', methods=['GET'])
@jwt_required()
def do_factors(factor_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()


        # پیدا کردن فاکتورهای مربوط به کاربر فعلی
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()
        if not factor or factor.status == 1:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد و یا قبلا پرداخت شده"}), 404


        MMERCHANT_ID = 'e359aef3-88b3-409b-b554-57fc5052705e'  # Required
        ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'  # Required
        amount = factor.price  # Amount will be based on Toman  Required
        description = u"پرداخت فاکتور" # Required
        email = user.email  # Optional
        mobile = user.phone # Optional
        client = Client(ZARINPAL_WEBSERVICE)
        print(f'5.34.195.27/Factors/did/{factor.id}')
        callback_url = url_for('factor.pardakht_factors', factor_id=factor.id, _external=True)

        result = client.service.PaymentRequest(MMERCHANT_ID,
                                               amount,
                                               description,
                                               email,
                                               mobile,
                                               callback_url)  # Use the
        if result.Status == 100:
            print(result)
            return {"status" : "okay", "Link_Pardakht" : 'https://www.zarinpal.com/pg/StartPay/' + result.Authority}, 200
        else:
            return {"status" : "error", "Link_Pardakht" : ''}, 500
    except Exception as e:
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در دریافت فاکتور"}), 500

@factors_bp.route('/Factors/Pardakht/<int:factor_id>', methods=['GET', 'POST'])
def pardakht_factors(factor_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()


        # پیدا کردن فاکتورهای مربوط به کاربر فعلی
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()
        if not factor or factor.status == 1:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد و یا قبلا پرداخت شده"}), 404

        MMERCHANT_ID = 'e359aef3-88b3-409b-b554-57fc5052705e'  # Required
        ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'  # Required
        amount = factor.price  # Amount will be based on Toman  Required

        client = Client(ZARINPAL_WEBSERVICE)
        if request.args.get('Status') == 'OK':
            result = client.service.PaymentVerification(MMERCHANT_ID,
                                                        request.args['Authority'],
                                                        amount)
            if result.Status == 100 or result.Status == 101:
                print(factor.status)
                factor.status = 1
                db.session.commit()

                factor_acsess = FactorAccess.query.filter_by(factor_id=factor.id).all()
                for factor_acsess_one in factor_acsess:
                    Users_in_Factors_Acsess_new = Users_in_Factors_Acsess(
                        user_id=user.id,
                        factor_id=factor.id,
                        Classifictions_id=factor_acsess_one.classifictions_for_factors_id,
                        expired_at=factor.expired_at
                    )
                    db.session.add(Users_in_Factors_Acsess_new)

                    classifictions_for_factors_id = factor_acsess_one.classifictions_for_factors_id
                    classifictions_user_accsess = PER_Classifictions_FOR_Factors.query.filter_by(
                        Classifictions_FOR_Factors_id_created=classifictions_for_factors_id).all()
                    for i in classifictions_user_accsess:
                        print(i.Classifictions_id_created)
                        new_user_acsses = UserAccess(
                            factor_id=factor.id,
                            user_id=user.id,
                            classifictions_id=i.Classifictions_id_created,
                            expired_at=factor.expired_at
                        )
                        db.session.add(new_user_acsses)
                        db.session.commit()

                flash('پرداخت شما با موفقیت انجام شد !')  # Flash a message
                return redirect("https://arkafile.org")

            else:
                flash('پرداخت شما با مشکل رو به رو شد !')  # Flash a message
                return redirect("https://arkafile.org")
        else:

            flash('پرداخت شما با مشکل رو به رو شد !')  # Flash a message
            return redirect("https://arkafile.org")



    except Exception as e:
        print(str(e))  # برای دیباگ
        flash('پرداخت شما با مشکل رو به رو شد !')  # Flash a message
        return redirect("https://arkafile.org")


@factors_bp.route('/Factors/did/<int:factor_id>', methods=['GET', 'POST'])
@jwt_required()
def did_factors(factor_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()


        # پیدا کردن فاکتورهای مربوط به کاربر فعلی
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()
        if not factor or factor.status == 1:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد و یا قبلا پرداخت شده"}), 404

        MMERCHANT_ID = 'e359aef3-88b3-409b-b554-57fc5052705e'  # Required
        ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'  # Required
        amount = factor.price  # Amount will be based on Toman  Required

        client = Client(ZARINPAL_WEBSERVICE)
        if request.args.get('Status') == 'OK':
            result = client.service.PaymentVerification(MMERCHANT_ID,
                                                        request.args['Authority'],
                                                        amount)
            if result.Status == 100 or result.Status == 101:
                print(factor.status)
                factor.status = 1
                db.session.commit()

                factor_acsess = FactorAccess.query.filter_by(factor_id=factor.id).all()
                for factor_acsess_one in factor_acsess:
                    Users_in_Factors_Acsess_new = Users_in_Factors_Acsess(
                        user_id=user.id,
                        factor_id=factor.id,
                        Classifictions_id=factor_acsess_one.classifictions_for_factors_id,
                        expired_at=factor.expired_at
                    )
                    db.session.add(Users_in_Factors_Acsess_new)

                    classifictions_for_factors_id = factor_acsess_one.classifictions_for_factors_id
                    classifictions_user_accsess = PER_Classifictions_FOR_Factors.query.filter_by(
                        Classifictions_FOR_Factors_id_created=classifictions_for_factors_id).all()
                    for i in classifictions_user_accsess:
                        print(i.Classifictions_id_created)
                        new_user_acsses = UserAccess(
                            factor_id=factor.id,
                            user_id=user.id,
                            classifictions_id=i.Classifictions_id_created,
                            expired_at=factor.expired_at
                        )
                        db.session.add(new_user_acsses)
                        db.session.commit()

                flash('پرداخت شما با موفقیت انجام شد !')  # Flash a message
                return redirect("https://arkafile.org")

            else:
                flash('پرداخت شما با مشکل رو به رو شد !')  # Flash a message
                return redirect("https://arkafile.org")
        else:

            flash('پرداخت شما با مشکل رو به رو شد !')  # Flash a message
            return redirect("https://arkafile.org")



    except Exception as e:
        print(str(e))  # برای دیباگ
        flash('پرداخت شما با مشکل رو به رو شد !')  # Flash a message
        return redirect("https://arkafile.org")

#--------------------------------------
# Routes Of manage factors
#--------------------------------------

@factors_bp.route('/Factors/Mange/<int:factor_id>', methods=['GET'])
@jwt_required()
def manage_factors(factor_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()


        # پیدا کردن فاکتورهای مربوط به کاربر فعلی
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()
        if not factor or factor.status != 1:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد"}), 404


        factor_acsess = FactorAccess.query.filter_by(factor_id=factor.id).all()
        acsess_dict = []
        for factor_acsess_one in factor_acsess:
            acsess = Classifictions_FOR_Factors.query.filter_by(id=factor_acsess_one.classifictions_for_factors_id).first()
            acsess_dict.append({"name":acsess.name, "ids":acsess.id})
        factors_dict = {
            "id": factor.id,
            "status": factor.status,
            "type": factor.type,
            "number": factor.number,
            "price": factor.price,
            "created_at": factor.created_at.isoformat(),
            "expired_at": factor.expired_at.isoformat()
        }
        return jsonify({"factor": factors_dict, "factor_acsess" : acsess_dict}), 200

    except Exception as e:
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در دریافت پول با پشتیبانی تماس بگیرید"}), 500

@factors_bp.route('/Factors/List/User/<int:factor_id>', methods=['GET'])
@jwt_required()
def manage_factors_list(factor_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()
        # پیدا کردن فاکتورهای مربوط به کاربر فعلی
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()
        if not factor or factor.status != 1:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد"}), 404
        reterun_list_users = []
        users_in_access = db.session.query(Users_in_Factors_Acsess, Users).join(
            Users, Users_in_Factors_Acsess.user_id == Users.id
        ).filter(Users_in_Factors_Acsess.factor_id == factor_id).all()
        unique_users = {}
        for access, user_data in users_in_access:
            # If the user_id is not in the set, add it to the dictionary
            if user_data.id not in unique_users:
                unique_users[user_data.id] = {
                    "user_id": user_data.id,
                    "user_phone": user_data.phone,
                    "user_name": user_data.name
                }
        return_list = []
        for v in unique_users.values():
            return_list.append(v)
        return return_list

    except Exception as e:
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در دریافت پول با پشتیبانی تماس بگیرید"}), 500


@factors_bp.route('/Factors/Acsess/Add/<int:user_phone_should_add>/<int:factor_id>', methods=['GET'])
@jwt_required()
def add_user_manage_factors_user_Acsses(factor_id, user_phone_should_add):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()
        user_should_add = Users.query.filter_by(phone=user_phone_should_add).first()
        # پیدا کردن فاکتورهای مربوط به کاربر فعلی
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()
        if not factor or factor.status != 1:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد"}), 404

        query = Users_in_Factors_Acsess.query.filter(Users_in_Factors_Acsess.factor_id == factor_id).all()

        unique_users = []
        for access in query:
            # If the user_id is not in the set, add it to the dictionary
            if access.id not in unique_users:
                unique_users.append(access.user_id)
        print(len(unique_users))
        print(unique_users)
        if user_should_add.id in unique_users or len(unique_users)+1 > factor.number:
            return jsonify({"message": "کاربر بیش از حد مجاز"}), 200


        factor_acsess = FactorAccess.query.filter_by(factor_id=factor.id).all()
        for factor_acsess_one in factor_acsess:
            Users_in_Factors_Acsess_new = Users_in_Factors_Acsess(
                user_id=user_should_add.id,
                factor_id=factor.id,
                Classifictions_id=factor_acsess_one.classifictions_for_factors_id,
                expired_at=factor.expired_at
            )
            db.session.add(Users_in_Factors_Acsess_new)

            classifictions_for_factors_id = factor_acsess_one.classifictions_for_factors_id
            classifictions_user_accsess = PER_Classifictions_FOR_Factors.query.filter_by(
                Classifictions_FOR_Factors_id_created=classifictions_for_factors_id).all()
            for i in classifictions_user_accsess:
                print(i.Classifictions_id_created)
                new_user_acsses = UserAccess(
                    factor_id=factor.id,
                    user_id=user_should_add.id,
                    classifictions_id=i.Classifictions_id_created,
                    expired_at=factor.expired_at
                )
                db.session.add(new_user_acsses)
                db.session.commit()

        return jsonify({"factors": "True"}), 200




    except Exception as e:
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در دریافت پول با پشتیبانی تماس بگیرید"}), 500


@factors_bp.route('/Factors/Acsess/Remove/<int:user_id>/<int:factor_id>', methods=['DELETE'])
@jwt_required()
def remove_user_manage_factors_user_access(user_id, factor_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر فعلی از دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()
        if not user:
            return jsonify({"message": "کاربر جاری یافت نشد"}), 404

        # پیدا کردن فاکتورهای مربوط به کاربر جاری
        factor = Factor.query.filter_by(id=factor_id, user_id=user.id).first()
        if not factor or factor.status != 1:
            return jsonify({"message": "فاکتور مورد نظر یافت نشد"}), 404

        # حذف کاربر از جدول Users_in_Factors_Acsess
        user_in_factor_access = Users_in_Factors_Acsess.query.filter_by(
            factor_id=factor_id, user_id=user_id).all()

        if not user_in_factor_access:
            return jsonify({"message": "کاربر مورد نظر یافت نشد یا حذف شده است"}), 404

        for user_access in user_in_factor_access:
            db.session.delete(user_access)

        # حذف دسترسی‌های کاربر از جدول UserAccess برای فاکتور مورد نظر
        user_access_list = UserAccess.query.filter_by(
            factor_id=factor_id, user_id=user_id).all()

        for user_access in user_access_list:
            db.session.delete(user_access)

        # اعمال تغییرات در دیتابیس
        db.session.commit()

        return jsonify({"message": "کاربر و دسترسی‌های مربوط با موفقیت حذف شد"}), 200

    except Exception as e:
        db.session.rollback()  # اگر خطایی رخ داد، تغییرات را برگردان
        print(str(e))  # برای دیباگ و شناسایی خطا
        return jsonify({"message": "خطای سرور. با پشتیبانی تماس بگیرید"}), 500
