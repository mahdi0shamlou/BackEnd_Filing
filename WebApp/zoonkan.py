from flask import Blueprint, jsonify, request
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import db, Posts
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

@zoonkan_bp.route('/ZoonKan/Edit', methods=['PUT'])
@jwt_required()
def edit_name_zoonkan():
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
    new_name = data.get('name')

    # بررسی وجود فیلدهای ضروری
    if not zoonkan_id or not new_name:
        return jsonify({"message": "لطفا تمام فیلدهای ضروری را وارد کنید!"}), 400

    # اعتبارسنجی نام جدید زونکن
    if len(new_name) < 3 or len(new_name) > 191:
        return jsonify({"message": "نام زونکن باید بین 3 تا 191 کاراکتر باشد!"}), 400

    # بررسی وجود زونکن
    zoonkan = ZoonKan.query.get(zoonkan_id)
    if not zoonkan:
        return jsonify({"message": "زونکن مورد نظر یافت نشد!"}), 404

    # بررسی مالکیت زونکن
    if zoonkan.user_id_created != user.id:
        return jsonify({"message": "شما اجازه دسترسی به این زونکن را ندارید!"}), 403

    try:
        # بروزرسانی نام زونکن
        zoonkan.name = new_name
        db.session.commit()

        return jsonify({
            "message": "نام زونکن با موفقیت بروزرسانی شد",
            "zoonkan": {
                "id": zoonkan.id,
                "name": zoonkan.name,
                "updated_at": zoonkan.updated_at.isoformat()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در بروزرسانی نام زونکن"}), 500

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
            file_id_created=file_id
        ).first()

        if existing_file:
            return jsonify({"message": "این فایل قبلاً به این زونکن اضافه شده است!"}), 400

        # اضافه کردن فایل به زونکن
        new_file_in_zoonkan = FilesInZoonKan(
            user_id_created=user.id,
            zoonkan_id_in=zoonkan_id,
            file_id_created=file_id
        )

        db.session.add(new_file_in_zoonkan)
        db.session.commit()

        return jsonify({
            "message": "فایل با موفقیت به زونکن اضافه شد",
            "file_in_zoonkan": {
                "id": new_file_in_zoonkan.id,
                "zoonkan_id": new_file_in_zoonkan.zoonkan_id_in,
                "file_id": new_file_in_zoonkan.file_id_created,
                "created_at": new_file_in_zoonkan.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(str(e))  # برای دیباگ
        return jsonify({"message": "خطا در اضافه کردن فایل به زونکن"}), 500

@zoonkan_bp.route('/ZoonKan/List', methods=['GET'])
@jwt_required()
def get_user_zoonkans():
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    user = Users.query.filter_by(phone=user_phone).first()
    if not user:
        return jsonify({"message": "کاربر یافت نشد!"}), 404

    # دریافت پارامترهای صفحه‌بندی
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # کوئری زونکن‌های کاربر
    query = ZoonKan.query.filter_by(user_id_created=user.id)

    zoonkans_pagination = query.order_by(ZoonKan.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    zoonkans = zoonkans_pagination.items

    zoonkans_list = [{
        'zoonkan_id': zoonkan.id,
        'name': zoonkan.name,
        'created_at': zoonkan.created_at,
    } for zoonkan in zoonkans]

    response_data = {
        'zoonkans': zoonkans_list,
        'pagination': {
            'current_page': page,
            'next_page': page + 1 if zoonkans_pagination.has_next else None,
            'previous_page': page - 1 if zoonkans_pagination.has_prev else None,
            'per_page': per_page,
            'total_zoonkans': zoonkans_pagination.total
        }
    }

    return jsonify(response_data)


@zoonkan_bp.route('/ZoonKan/<int:zoonkan_id>/Files', methods=['GET'])
@jwt_required()
def get_zoonkan_files(zoonkan_id):
    try:
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        user = Users.query.filter_by(phone=user_phone).first()
        if not user:
            return jsonify({"message": "کاربر یافت نشد!"}), 404

        # بررسی وجود و دسترسی به زونکن
        zoonkan = ZoonKan.query.filter_by(id=zoonkan_id).first()

        if not zoonkan:
            return jsonify({"message": "زونکن مورد نظر یافت نشد!"}), 404

        if zoonkan.user_id_created != user.id:
            return jsonify({"message": "شما به این زونکن دسترسی ندارید!"}), 403

        # دریافت پارامترهای صفحه‌بندی
        page = request.args.get('page', 1, type=int)
        #per_page = request.args.get('per_page', 10, type=int)
        per_page = 1000
        # کوئری فایل‌های زونکن با جوین Posts
        query = db.session.query(FilesInZoonKan, Posts).join(Posts, FilesInZoonKan.file_id_created == Posts.id).filter(FilesInZoonKan.zoonkan_id_in == zoonkan_id)

        files_pagination = query.order_by(FilesInZoonKan.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        files = files_pagination.items

        files_list = [{
            'file_id': file.FilesInZoonKan.file_id_created,
            'added_by': file.FilesInZoonKan.user_id_created,
            'added_at': file.FilesInZoonKan.created_at,
            'post_data': {
                'id': file.Posts.id,
                'title': file.Posts.title,
                'Images': file.Posts.Images,
                'city': file.Posts.city_text,
                'type': file.Posts.type_text,
                '_type': str(file.Posts.type)[0],
                'price': file.Posts.price,
                'price_two': file.Posts.price_two,
                'PARKING': file.Posts.PARKING,
                'CABINET': file.Posts.CABINET,
                'ELEVATOR': file.Posts.ELEVATOR,
                'Otagh': file.Posts.Otagh,
                'Make_years': file.Posts.Make_years,
                'phone': file.Posts.number,
                'mahal': file.Posts.mahal_text,
                'meter': file.Posts.meter,
                'token': file.Posts.token,
                'desck': file.Posts.desck,
                'details': file.Posts.details,
                'date_created_persian': file.Posts.date_created_persian
            }
        } for file in files]

        response_data = {
            'files': files_list,
            'pagination': {
                'current_page': page,
                'next_page': page + 1 if files_pagination.has_next else None,
                'previous_page': page - 1 if files_pagination.has_prev else None,
                'per_page': per_page,
                'total_files': files_pagination.total
            }
        }

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"message": f"error"}), 500


@zoonkan_bp.route('/ZoonKan/Delete/<int:zoonkan_id>', methods=['DELETE'])
@jwt_required()
def delete_zoonkan(zoonkan_id):
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # یافتن کاربر
    user = Users.query.filter_by(phone=user_phone).first()
    if not user:
        return jsonify({"message": "کاربر یافت نشد!"}), 404

    # یافتن زونکن
    zoonkan = ZoonKan.query.filter_by(id=zoonkan_id, user_id_created=user.id).first()
    if not zoonkan:
        return jsonify({"message": "زونکن یافت نشد یا شما دسترسی به آن ندارید!"}), 404

    try:
        db.session.delete(zoonkan)
        db.session.commit()
        return jsonify({"message": "زونکن با موفقیت حذف شد"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "خطا در حذف زونکن"}), 500


@zoonkan_bp.route('/ZoonKan/RemoveFile/<int:zoonkan_id>/<int:file_id>', methods=['DELETE'])
@jwt_required()
def remove_file_from_zoonkan(zoonkan_id, file_id):
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # یافتن کاربر
    user = Users.query.filter_by(phone=user_phone).first()
    if not user:
        return jsonify({"message": "کاربر یافت نشد!"}), 404

    # یافتن فایل در زونکن
    file_in_zoonkan = FilesInZoonKan.query.filter_by(
        zoonkan_id_in=zoonkan_id,
        file_id_created=file_id,
        user_id_created=user.id
    ).first()

    if not file_in_zoonkan:
        return jsonify({"message": "فایل در زونکن یافت نشد یا شما دسترسی به آن ندارید!"}), 404

    try:
        db.session.delete(file_in_zoonkan)
        db.session.commit()
        return jsonify({"message": "فایل با موفقیت از زونکن حذف شد"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "خطا در حذف فایل از زونکن"}), 500


