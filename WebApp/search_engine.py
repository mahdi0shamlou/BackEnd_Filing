from flask import request
from datetime import datetime
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


def check_user_has_accses_new_version(user, request):
    try:
        #---------------------
        # get user Access
        # ---------------------
        user_access_ids = UserAccess.query.filter_by(user_id=user.id).with_entities(
            UserAccess.classifictions_id).distinct().all()

        if not user_access_ids:
            return False, [], []
        list_search = [classification[0] for classification in user_access_ids]
        #---------------------
        # pars request data
        # ---------------------
        request_data = request.get_json()
        #---------------------
        # check user type and mahal Access
        # ---------------------
        requested_types = request_data.get('type', [])  # دریافت به صورت لیست
        requested_mahal = request_data.get('mahal', [])  # دریافت به صورت لیست
        # اگر types درخواستی خالی باشد، تمام types مجاز را برمی‌گردانیم
        if not requested_types:
            return False, [], []
        if not requested_mahal:
            return False, [], []
        # دریافت تمام type های مجاز برای این classification
        allowed_types = (db.session.query(ClassificationTypes.type)
                         .filter(ClassificationTypes.classifiction_id.in_(list_search))
                         .distinct()
                         .all())
        # Retrieve unique allowed neighborhood IDs directly
        allowed_mahal = (db.session.query(ClassificationNeighborhood.neighborhood_id)
                         .filter(ClassificationNeighborhood.classifiction_id.in_(list_search))
                         .distinct()
                         .all())

        allowed_types_flat = [classification[0] for classification in allowed_types]
        allowed_mahal_flat = [classification[0] for classification in allowed_mahal]

        # چک می‌کنیم آیا تمام types درخواستی در لیست مجاز هستند
        for type_id in requested_types:
            if type_id not in allowed_types_flat:
                return False, [], []

        for mahal_id in requested_mahal:
            if mahal_id not in allowed_mahal_flat:
                return False, [], []

        print(f"this is lis of user_access {list_search}")
        print(f"mahal_id should search {requested_mahal} search in {allowed_mahal_flat}")
        print(f"type_id should search {requested_types} search in {allowed_types_flat}")

        return True, requested_mahal, requested_types

    except Exception as e:
        print(f"Error in check_user_has_accses: {str(e)}")
        return False, [], []

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
        auth_header = request.headers.get('Authorization', None)
        auth_header = auth_header.split(" ")[1]
        if auth_header == user.jwt_token:
            # بررسی دسترسی کاربر و دریافت محله‌های مجاز
            has_access, allowed_mahals, allowed_type_ids = check_user_has_accses(user, request)
            if not has_access:
                return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403


            try:
                is_active = request_data.get('is_active', True)
                phone_number = request_data.get('phone_number', None)
                post_id = request_data.get('post_id', None)
                price_from = request_data.get('price_from', None)
                price_to = request_data.get('price_to', None)
                price_from_two = request_data.get('price_from_2', None)
                price_to_two = request_data.get('price_to_2', None)
                meter_from = request_data.get('meter_from', None)
                meter_to = request_data.get('meter_to', None)
                page = request_data.get('page', 1)
                otagh = request_data.get('otagh', None)
                make_from = request_data.get('make_from', None)
                make_to = request_data.get('make_two', None)
                desck = request_data.get('desck', None)
                date_start = request_data.get('date_start', None)
                date_end = request_data.get('date_end', None)


                query = Posts.query.filter(Posts.status == 1)
                query = query.filter(Posts.is_active == is_active)
                query = query.filter(Posts.mahal.in_(allowed_mahals))
                print(allowed_type_ids)

                if post_id is not None:
                    query = query.filter(Posts.id == post_id)
                if phone_number is not None:
                    query = query.filter(Posts.number == phone_number)

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

                if date_start is not None:
                    query = query.filter(Posts.date_created >= datetime.strptime(date_start, '%Y-%m-%d'))

                if date_end is not None:
                    query = query.filter(Posts.date_created <= datetime.strptime(date_end, '%Y-%m-%d'))


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
                    'desck': post.desck,
                    'date_created': post.date_created
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
        else:
            return jsonify({'error': 'An error occurred', 'message': "شما احتمالا با چند دیوایس مختلف وارد شده اید !"}), 500

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
        auth_header = request.headers.get('Authorization', None)
        auth_header = auth_header.split(" ")[1]
        if auth_header == user.jwt_token:
            # بررسی دسترسی کاربر و دریافت محله‌های مجاز
            has_access, allowed_mahals, allowed_type_ids = check_user_has_accses(user, request)
            if not has_access:
                return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403


            try:
                is_active = request_data.get('is_active', True)
                phone_number = request_data.get('phone_number', None)
                post_id = request_data.get('post_id', None)
                price_from = request_data.get('price_from', None)
                price_to = request_data.get('price_to', None)
                price_from_two = request_data.get('price_from_2', None)
                price_to_two = request_data.get('price_to_2', None)
                meter_from = request_data.get('meter_from', None)
                meter_to = request_data.get('meter_to', None)
                page = request_data.get('page', 1)
                otagh = request_data.get('otagh', None)
                make_from = request_data.get('make_from', None)
                make_to = request_data.get('make_two', None)
                desck = request_data.get('desck', None)
                date_start = request_data.get('date_start', None)
                date_end = request_data.get('date_end', None)


                query = Posts.query.filter(Posts.status == 1)
                query = query.filter(Posts.is_active == is_active)
                query = query.filter(Posts.mahal.in_(allowed_mahals))
                print(allowed_type_ids)

                if post_id is not None:
                    query = query.filter(Posts.id == post_id)
                if phone_number is not None:
                    query = query.filter(Posts.number == phone_number)

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

                if date_start is not None:
                    query = query.filter(Posts.date_created >= datetime.strptime(date_start, '%Y-%m-%d'))

                if date_end is not None:
                    query = query.filter(Posts.date_created <= datetime.strptime(date_end, '%Y-%m-%d'))

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
                    'BALCONY': query.BALCONY,
                    'Otagh': query.Otagh,
                    'Make_years': query.Make_years,
                    'phone': query.number,
                    'mahal': query.mahal_text,
                    'meter': query.meter,
                    'token': query.token,
                    'desck': query.desck,
                    'details': query.details,
                    'floor': query.floor,
                    'dwelling_units_per_floor': query.dwelling_units_per_floor,
                    'dwelling_unit_floor': query.dwelling_unit_floor,
                    'wc': query.wc,
                    'floor_type': query.floor_type,
                    'water_provider': query.water_provider,
                    'cool': query.cool,
                    'heat': query.heat,
                    '_map': True if query.map else False,
                    'building_directions': query.building_directions,
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
        else:
            return jsonify({'error': 'An error occurred', 'message': "شما احتمالا با چند دیوایس مختلف وارد شده اید !"}), 500
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


"""
@searchenign_bp.route('/Search/User/Class', methods=['POST'])
@jwt_required()
def users_access_class_new():
    try:
        request_data = request.get_json()
        type_search = request_data.get('type_search', 1) # sell => 1 , rent => 2

        # دریافت اطلاعات کاربر از توکن
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'کاربر یافت نشد'
            }), 404

        user_access_ids = UserAccess.query.filter_by(user_id=user.id).with_entities(
            UserAccess.classifictions_id).distinct().all()

        if not user_access_ids:
            return jsonify({
                'status': 'error',
                'message': 'شما دسترسی به این دسته‌بندی ندارید'
            }), 403
        list_search = [classification[0] for classification in user_access_ids]
        list_search_res = (db.session.query(Classification.id).filter(Classification.types==type_search)
                         .filter(Classification.id.in_(list_search))
                         .distinct()
                         .all())
        list_should_search = [classification[0] for classification in list_search_res]

        # دریافت تمام type های مجاز برای این classification
        allowed_types = (db.session.query(ClassificationTypes.type)
                         .filter(ClassificationTypes.classifiction_id.in_(list_should_search))
                         .distinct()
                         .all())
        # Retrieve unique allowed neighborhood IDs directly
        allowed_mahal = (db.session.query(ClassificationNeighborhood.neighborhood_id)
                         .filter(ClassificationNeighborhood.classifiction_id.in_(list_should_search))
                         .distinct()
                         .all())
        print(allowed_mahal)
        print(allowed_types)
        allowed_types_flat = [classification[0] for classification in allowed_types]
        allowed_mahal_flat = [classification[0] for classification in allowed_mahal]


        types = Types_file.query.filter(Types_file.id.in_(allowed_types_flat)).all()

        types_list = [{
            'id': type.id,
            'name': type.name
        } for type in types]

        neighborhoods = Neighborhood.query.filter(Neighborhood.id.in_(allowed_mahal_flat)).all()

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
"""
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

#-------------------------------------
# First page serach requests
#-------------------------------------

def user_acsses_for_first_pages(user):
    try:

        access = UserAccess.query.filter_by(
            user_id=user.id,
        ).all()

        if not access:
            return False, [], []

        # دریافت تمام type های مجاز برای این classification
        allowed_types = (db.session.query(ClassificationTypes.type)
                         .filter(ClassificationTypes.classifiction_id == access[0].id)
                         .all())

        allowed_type_ids = [t[0] for t in allowed_types]


        # دریافت محله‌های مجاز
        allowed_neighborhoods = (db.session.query(Neighborhood.id)
                                 .join(ClassificationNeighborhood)
                                 .filter(ClassificationNeighborhood.classifiction_id == access[0].id)
                                 .all())

        allowed_neighborhood_ids = [n[0] for n in allowed_neighborhoods]

        return True, allowed_neighborhood_ids, allowed_type_ids

    except Exception as e:
        print(f"Error in check_user_has_accses: {str(e)}")
        return False, [], []

@searchenign_bp.route('/Search/FullDetails/FirstPage', methods=['POST'])
@jwt_required()
def full_details_first_page():
    try:
        request_data = request.get_json()
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()
        auth_header = request.headers.get('Authorization', None)
        auth_header = auth_header.split(" ")[1]
        if auth_header == user.jwt_token:

            # بررسی دسترسی کاربر و دریافت محله‌های مجاز
            has_access, allowed_mahals, allowed_type_ids = user_acsses_for_first_pages(user)
            if not has_access:
                return jsonify({"message": "شما اشتراک فعالی ندارید !"}), 403
            page = request_data.get('page', 1)

            query = Posts.query.filter(Posts.status == 1)
            query = query.filter(Posts.type.in_(allowed_type_ids))
            query = query.filter(Posts.mahal.in_(allowed_mahals))
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
                'BALCONY': query.BALCONY,
                'Otagh': query.Otagh,
                'Make_years': query.Make_years,
                'phone': query.number,
                'mahal': query.mahal_text,
                'meter': query.meter,
                'token': query.token,
                'desck': query.desck,
                'details': query.details,
                'floor': query.floor,
                'dwelling_units_per_floor': query.dwelling_units_per_floor,
                'dwelling_unit_floor': query.dwelling_unit_floor,
                'wc': query.wc,
                'floor_type': query.floor_type,
                'water_provider': query.water_provider,
                'cool': query.cool,
                'heat': query.heat,
                'building_directions': query.building_directions,
                'date_created_persian': query.date_created_persian,
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

        else:
            return jsonify(
                {'error': 'An error occurred', 'message': "شما احتمالا با چند دیوایس مختلف وارد شده اید !"}), 500
    except Exception as e:
        print(e)
        return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره امتحان کنید !', 'message': str(e)}), 500


#-------------------------
# --- map
#-------------------------
import json

@searchenign_bp.route('/Search/FullDetails/Map/<int:post_id>', methods=['POST'])
@jwt_required()
def full_details_map_lat_lang(post_id):
    try:
        request_data = request.get_json()
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401
        auth_header = auth_header.split(" ")[1]
        if auth_header == user.jwt_token:
            """
            # بررسی دسترسی کاربر و دریافت محله‌های مجاز
            has_access, allowed_mahals, allowed_type_ids = user_acsses_for_first_pages(user)
            if not has_access:
                return jsonify({"message": "شما اشتراک فعالی ندارید !"}), 403
            """
            class_x = request_data.get('class', 1)

            query = Posts.query.filter(Posts.id == post_id).first()

            if query is None:
                return jsonify({'message': 'Post not found'}), 404

            response_data = {}

            if query.map:
                try:
                    sanitized_map_string = query.map.replace("'", '"')

                    map_data = json.loads(sanitized_map_string)  # Parse JSON from the text column


                    widgets = map_data.get('widgets')
                    if widgets and isinstance(widgets, list) and len(widgets) > 0:
                        first_widget = widgets[0]
                        if isinstance(first_widget, dict) and first_widget.get('widget_type') == 'MAP_ROW':
                            data = first_widget.get('data')
                            if isinstance(data, dict):
                                location = data.get('location')
                                if isinstance(location, dict) and location.get('type') == 'FUZZY':
                                    fuzzy_data = location.get('fuzzy_data')
                                    if isinstance(fuzzy_data, dict):
                                        point = fuzzy_data.get('point')
                                        if isinstance(point, dict):
                                            response_data['latitude'] = point.get('latitude')
                                            response_data['longitude'] = point.get('longitude')
                                        else:
                                            response_data['latitude'] = None
                                            response_data['longitude'] = None
                                    else:
                                        response_data['latitude'] = None
                                        response_data['longitude'] = None
                                else:
                                    response_data['latitude'] = None
                                    response_data['longitude'] = None
                            else:
                                response_data['latitude'] = None
                                response_data['longitude'] = None
                        else:
                            response_data['latitude'] = None
                            response_data['longitude'] = None
                    else:
                        response_data['latitude'] = None
                        response_data['longitude'] = None
                except (KeyError, AttributeError, TypeError, json.JSONDecodeError) as e:
                    print(f"Error extracting coordinates: {e}")
                    response_data['latitude'] = None
                    response_data['longitude'] = None
            else:
                response_data['latitude'] = None
                response_data['longitude'] = None

            return jsonify(response_data)

        else:
            return jsonify(
                {'error': 'An error occurred', 'message': "شما احتمالا با چند دیوایس مختلف وارد شده اید !"}), 500
    except Exception as e:
        print(e)
        return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره امتحان کنید !', 'message': str(e)}), 500

