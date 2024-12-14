from flask import request
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, make_response
#-------------
#------------- models
from models import users as Users
from models import Posts
from sqlalchemy import or_
from models import db
from models import Classification, ClassificationNeighborhood, Neighborhood, UserAccess, ClassificationTypes, Types_file
#---------------

searchenign_bp = Blueprint('searchenign', __name__)


def check_user_has_accses(user, request):
    try:
        request_data = request.get_json()
        class_id = request_data.get('class', 1)
        requested_types = request_data.get('type', [])  # دریافت به صورت لیست

        # چک کردن دسترسی کاربر به classification
        access = UserAccess.query.filter_by(
            user_id=user.id,
            classifictions_id=class_id
        ).first()

        if not access:
            return False, [], []

        # دریافت تمام type های مجاز برای این classification
        allowed_types = (db.session.query(ClassificationTypes.type)
                         .filter(ClassificationTypes.classifiction_id == class_id)
                         .all())

        allowed_type_ids = [t[0] for t in allowed_types]

        # اگر types درخواستی خالی باشد، تمام types مجاز را برمی‌گردانیم
        if not requested_types:
            requested_types = allowed_type_ids
        # اگر types درخواستی آرایه نیست، تبدیل به آرایه می‌کنیم
        elif not isinstance(requested_types, list):
            requested_types = [requested_types]

        # چک می‌کنیم آیا تمام types درخواستی در لیست مجاز هستند
        for type_id in requested_types:
            if type_id not in allowed_type_ids:
                return False, [], []

        # دریافت محله‌های مجاز
        allowed_neighborhoods = (db.session.query(Neighborhood.id)
                                 .join(ClassificationNeighborhood)
                                 .filter(ClassificationNeighborhood.classifiction_id == class_id)
                                 .all())

        allowed_neighborhood_ids = [n[0] for n in allowed_neighborhoods]

        # چک کردن محله‌های درخواستی
        requested_mahals = request_data.get('mahal', [])
        if requested_mahals:
            for mahal in requested_mahals:
                if mahal not in allowed_neighborhood_ids:
                    return False, [], []
            return True, requested_mahals, requested_types
        else:
            return True, allowed_neighborhood_ids, requested_types

    except Exception as e:
        print(f"Error in check_user_has_accses: {str(e)}")
        return False, [], []


@searchenign_bp.route('/Search/LessDetails', methods=['POST'])
@jwt_required()
def search_engine_less_details():
    try:
        request_data = request.get_json()
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()

        # بررسی دسترسی کاربر و دریافت محله‌های مجاز
        has_access, allowed_mahals, allowed_type_ids = check_user_has_accses(user, request)
        if not has_access:
            return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403


        try:
            price_from = request_data.get('price_from', None)
            price_to = request_data.get('price_to', None)
            price_from_two = request_data.get('price_from_2', None)
            price_to_two = request_data.get('price_to_2', None)
            meter_from = request_data.get('meter_from', None)
            meter_to = request_data.get('meter_to', None)
            page = request_data.get('page', 1)
            otagh = request_data.get('otagh', None)
            make_from = request_data.get('make_from')
            make_to = request_data.get('make_two')
            desck = request_data.get('desck', None)


            query = Posts.query.filter(Posts.status == 1)
            query = query.filter(Posts.mahal.in_(allowed_mahals))
            print(allowed_type_ids)

            if allowed_type_ids:
                query = query.filter(Posts.type.in_(allowed_type_ids))

            if price_from is not None and price_to is not None:
                query = query.filter(Posts.price.between(price_from, price_to))
            elif price_from is not None:
                query = query.filter(Posts.price >= price_from)
            elif price_to is not None:
                query = query.filter(Posts.price <= price_to)

            if price_from_two is not None and price_to_two is not None:
                query = query.filter(Posts.price_two.between(price_from_two, price_to_two))
            elif price_from_two is not None:
                query = query.filter(Posts.price_two >= price_from_two)
            elif price_to_two is not None:
                query = query.filter(Posts.price_two <= price_to_two)

            if meter_from is not None and meter_to is not None:
                query = query.filter(Posts.meter.between(meter_from, meter_to))
            elif meter_from is not None:
                query = query.filter(Posts.meter >= meter_from)
            elif meter_to is not None:
                query = query.filter(Posts.meter <= meter_to)

            if otagh is not None:
                if otagh != -1:
                    query = query.filter(Posts.Otagh == otagh)

            if make_from is not None and make_to is not None:
                query = query.filter(Posts.Make_years.between(make_from, make_to))
            elif make_from is not None:
                query = query.filter(Posts.Make_years >= make_from)
            elif make_to is not None:
                query = query.filter(Posts.Make_years <= make_to)

            if 'parking' in request_data:
                query = query.filter(Posts.PARKING == True)

            if 'cabinet' in request_data:
                query = query.filter(Posts.CABINET == True)

            if 'elevator' in request_data:
                query = query.filter(Posts.ELEVATOR == True)

            if desck is not None:
                query = query.filter(or_(
                    Posts.desck.ilike(f'%{desck}%'),
                    Posts.title.ilike(f'%{desck}%')
                ))

            per_page = 12

            posts_pagination = query.order_by(Posts.id.desc()).paginate(page=page, per_page=per_page,
                                                                        error_out=False)

            posts = posts_pagination.items
            # Build a list of post details to send in the response
            posts_list = [{
                'id': post.id,
                'title': post.title,
                'city': post.city_text,
                'price': post.price,
                'price_two': post.price_two,
                'mahal': post.mahal_text,
                'meter': post.meter,
                'token': post.token,
                'desck': post.desck[:30],
                'date_created': query.date_created
            } for post in posts]

            response_data = {
                'posts': posts_list,
                'pagination': {
                    'current_page': page,
                    'next_page': page + 1 if posts_pagination.has_next else None,
                    'previous_page': page - 1 if posts_pagination.has_prev else None,
                    'per_page': per_page,
                    'total_posts': posts_pagination.total
                }
            }


            return jsonify(response_data)
        except Exception as e:
            print(e)  # Log the error
            return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

    except Exception as e:
        print(e)
        return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره امتحان کنید !', 'message': str(e)}), 500

#-------------------------------------
# telegram view
#-------------------------------------
@searchenign_bp.route('/Search/FullDetails', methods=['POST'])
@jwt_required()
def search_engine_full_details():
    try:
        request_data = request.get_json()
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()

        # بررسی دسترسی کاربر و دریافت محله‌های مجاز
        has_access, allowed_mahals, allowed_type_ids = check_user_has_accses(user, request)
        if not has_access:
            return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403


        try:
            price_from = request_data.get('price_from', None)
            price_to = request_data.get('price_to', None)
            price_from_two = request_data.get('price_from_2', None)
            price_to_two = request_data.get('price_to_2', None)
            meter_from = request_data.get('meter_from', None)
            meter_to = request_data.get('meter_to', None)
            page = request_data.get('page', 1)
            otagh = request_data.get('otagh', None)
            make_from = request_data.get('make_from')
            make_to = request_data.get('make_two')
            desck = request_data.get('desck', None)


            query = Posts.query.filter(Posts.status == 1)
            query = query.filter(Posts.mahal.in_(allowed_mahals))
            print(allowed_type_ids)

            if allowed_type_ids:
                query = query.filter(Posts.type.in_(allowed_type_ids))

            if price_from is not None and price_to is not None:
                query = query.filter(Posts.price.between(price_from, price_to))
            elif price_from is not None:
                query = query.filter(Posts.price >= price_from)
            elif price_to is not None:
                query = query.filter(Posts.price <= price_to)

            if price_from_two is not None and price_to_two is not None:
                query = query.filter(Posts.price_two.between(price_from_two, price_to_two))
            elif price_from_two is not None:
                query = query.filter(Posts.price_two >= price_from_two)
            elif price_to_two is not None:
                query = query.filter(Posts.price_two <= price_to_two)

            if meter_from is not None and meter_to is not None:
                query = query.filter(Posts.meter.between(meter_from, meter_to))
            elif meter_from is not None:
                query = query.filter(Posts.meter >= meter_from)
            elif meter_to is not None:
                query = query.filter(Posts.meter <= meter_to)

            if otagh is not None:
                if otagh != -1:
                    query = query.filter(Posts.Otagh == otagh)

            if make_from is not None and make_to is not None:
                query = query.filter(Posts.Make_years.between(make_from, make_to))
            elif make_from is not None:
                query = query.filter(Posts.Make_years >= make_from)
            elif make_to is not None:
                query = query.filter(Posts.Make_years <= make_to)


            if 'parking' in request_data:
                query = query.filter(Posts.PARKING == True)

            if 'cabinet' in request_data:
                query = query.filter(Posts.CABINET == True)

            if 'elevator' in request_data:
                query = query.filter(Posts.ELEVATOR == True)

            if desck is not None:
                query = query.filter(or_(
                    Posts.desck.ilike(f'%{desck}%'),
                    Posts.title.ilike(f'%{desck}%')
                ))

            per_page = 12


            posts_pagination = query.order_by(Posts.id.desc()).paginate(page=page, per_page=per_page,
                                                                                   error_out=False)

            posts = posts_pagination.items

            # Build a list of post details to send in the response
            posts_list = [{
                'id': query.id,
                'title': query.title,
                'Images': query.Images,
                'city': query.city_text,
                'type': query.type_text,
                '_type': str(query.type)[0],
                'price': query.price,
                'price_two': query.price_two,
                'PARKING': query.PARKING,
                'CABINET': query.CABINET,
                'ELEVATOR': query.ELEVATOR,
                'Otagh': query.Otagh,
                'Make_years': query.Make_years,
                'phone': query.number,
                'mahal': query.mahal_text,
                'meter': query.meter,
                'token': query.token,
                'desck': query.desck,
                'details': query.details,
                'date_created_persian':query.date_created_persian,
                'date_created': query.date_created
            } for query in posts]

            response_data = {
                'posts': posts_list,
                'pagination': {
                    'current_page': page,
                    'next_page': page + 1 if posts_pagination.has_next else None,
                    'previous_page': page - 1 if posts_pagination.has_prev else None,
                    'per_page': per_page,
                    'total_posts': posts_pagination.total
                }
            }


            return jsonify(response_data)
        except Exception as e:
            print(e)  # Log the error
            return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

    except Exception as e:
        print(e)
        return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره امتحان کنید !', 'message': str(e)}), 500


#-------------------------------------
# mahal requests
#-------------------------------------

@searchenign_bp.route('/Search/User/Access', methods=['GET'])
@jwt_required()
def users_access():
    try:
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()

        #results = get_user_neighborhoods_access_2(user.id)
        #print(results)

        # دریافت دسته‌بندی‌های کاربر با استفاده از join
        classifications = db.session.query(Classification)\
            .join(UserAccess, UserAccess.classifictions_id == Classification.id)\
            .filter(UserAccess.user_id == user.id)\
            .all()


        results = []
        for classification in classifications:
            results.append({
                'id': classification.id,
                'name': classification.name,
                'created_at': classification.created_at.strftime('%Y-%m-%d %H:%M:%S') if classification.created_at else None,
                'updated_at': classification.updated_at.strftime('%Y-%m-%d %H:%M:%S') if classification.updated_at else None
            })

        if results is None:
            return make_response(jsonify({
                'status': 'error',
                'message': 'An error occurred while fetching data'
            }), 500)

        return make_response(jsonify({
            'status': 'success',
            'data': results
        }), 200)

    except Exception as e:
        return make_response(jsonify({
            'status': 'error',
            'message': str(e)
        }), 500)


@searchenign_bp.route('/Search/User/Class', methods=['POST'])
@jwt_required()
def users_access_class_new():
    try:
        request_data = request.get_json()
        classification_id = request_data.get('class', 1)

        # دریافت اطلاعات کاربر از توکن
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'کاربر یافت نشد'
            }), 404

        # چک کردن دسترسی کاربر
        access = UserAccess.query.filter_by(
            user_id=user.id,
            classifictions_id=classification_id
        ).first()

        if not access:
            return jsonify({
                'status': 'error',
                'message': 'شما دسترسی به این دسته‌بندی ندارید'
            }), 403

        # Get classification types with their names
        types = (db.session.query(
            ClassificationTypes.type,
            Types_file.name.label('type_name')
        )
                 .join(Types_file, ClassificationTypes.type == Types_file.id)
                 .filter(ClassificationTypes.classifiction_id == classification_id)
                 .all())

        types_list = [{
            'id': type.type,
            'name': type.type_name
        } for type in types]

        # Get neighborhoods through ClassificationNeighborhood
        neighborhoods = (db.session.query(Neighborhood)
                         .join(ClassificationNeighborhood)
                         .filter(ClassificationNeighborhood.classifiction_id == classification_id)
                         .all())

        neighborhoods_list = [{
            'id': neighborhood.id,
            'name': neighborhood.name
        } for neighborhood in neighborhoods]

        response = {
            'status': 'success',
            'data': {
                'types': types_list,
                'neighborhoods': neighborhoods_list
            }
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
