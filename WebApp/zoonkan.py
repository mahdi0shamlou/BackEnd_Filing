from flask import Blueprint, jsonify, request
import re
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import db
from models import ZoonKan
from models import FilesInZoonKan
# ---------------

zoonkan_bp = Blueprint('zoonkan', __name__)

@zoonkan_bp.route('/ZoonKan/Create', methods=['POST'])
@jwt_required()
def create_zoonkan():
    # دریافت اطلاعات کاربر فعلی از توکن JWT
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # پیدا کردن کاربر در دیتابیس
    user = Users.query.filter_by(phone=user_phone).first()

    if not user:
        return jsonify({"message": "خطا کاربر مورد نظر یافت نشد!"}), 404

    # دریافت داده‌های ارسالی
    data = request.get_json()

    if not data:
        return jsonify({"message": "داده‌ای دریافت نشد!"}), 400

    zoonkan_name = data.get('name')

    # بررسی وجود نام زونکن
    if not zoonkan_name:
        return jsonify({"message": "لطفا نام زونکن را وارد کنید!"}), 400

    # اعتبارسنجی نام زونکن
    if len(zoonkan_name) < 3 or len(zoonkan_name) > 191:
        return jsonify({"message": "نام زونکن باید بین 3 تا 191 کاراکتر باشد!"}), 400

    try:
        # ایجاد زونکن جدید
        new_zoonkan = ZoonKan(
            user_id_created=user.id,
            name=zoonkan_name
        )

        db.session.add(new_zoonkan)
        db.session.commit()

        return jsonify({
            "message": "زونکن با موفقیت ایجاد شد",
            "zoonkan": {
                "id": new_zoonkan.id,
                "name": new_zoonkan.name,
                "created_at": new_zoonkan.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در ایجاد زونکن"}), 500

@zoonkan_bp.route('/ZoonKan/AddFile', methods=['POST'])
@jwt_required()
def add_file_to_zoonkan():
    # دریافت اطلاعات کاربر فعلی از توکن JWT
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # پیدا کردن کاربر در دیتابیس
    user = Users.query.filter_by(phone=user_phone).first()

    if not user:
        return jsonify({"message": "خطا کاربر مورد نظر یافت نشد!"}), 404

    # دریافت داده‌های ارسالی
    data = request.get_json()

    if not data:
        return jsonify({"message": "داده‌ای دریافت نشد!"}), 400

    zoonkan_id = data.get('zoonkan_id')
    file_id = data.get('file_id')

    # بررسی وجود فیلدهای ضروری
    if not zoonkan_id or not file_id:
        return jsonify({"message": "لطفا تمام فیلدهای ضروری را وارد کنید!"}), 400

    # بررسی وجود زونکن
    zoonkan = ZoonKan.query.get(zoonkan_id)
    if not zoonkan:
        return jsonify({"message": "زونکن مورد نظر یافت نشد!"}), 404

    # بررسی مالکیت زونکن
    if zoonkan.user_id_created != user.id:
        return jsonify({"message": "شما اجازه دسترسی به این زونکن را ندارید!"}), 403

    try:
        # بررسی تکراری نبودن فایل در زونکن
        existing_file = FilesInZoonKan.query.filter_by(
            zoonkan_id_in=zoonkan_id,
            file_id=file_id
        ).first()

        if existing_file:
            return jsonify({"message": "این فایل قبلاً به این زونکن اضافه شده است!"}), 400

        # اضافه کردن فایل به زونکن
        new_file_in_zoonkan = FilesInZoonKan(
            user_id_created=user.id,
            zoonkan_id_in=zoonkan_id,
            file_id=file_id
        )

        db.session.add(new_file_in_zoonkan)
        db.session.commit()

        return jsonify({
            "message": "فایل با موفقیت به زونکن اضافه شد",
            "file_in_zoonkan": {
                "id": new_file_in_zoonkan.id,
                "zoonkan_id": new_file_in_zoonkan.zoonkan_id_in,
                "file_id": new_file_in_zoonkan.file_id,
                "created_at": new_file_in_zoonkan.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در اضافه کردن فایل به زونکن"}), 500
