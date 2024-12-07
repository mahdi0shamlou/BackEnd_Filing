from flask import request, Blueprint, jsonify
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
#-------------
#------------- models
from models import users as Users
from models import Posts
from sqlalchemy import or_
#---------------

searchenign_bp = Blueprint('searchenign', __name__)

def check_user_has_accses(user, mahal):
    print(user)
    print(mahal)
    return True


@searchenign_bp.route('/Search/LessDetails', methods=['POST'])
@jwt_required()
def search_engine_less_details():
    try:
        # Parse JSON body
        request_data = request.get_json()

        # Default values, can be overridden by JSON body
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()
        check_accses = check_user_has_accses(user, 0)
        if check_accses:
            try:
                city = request_data.get('city', 1)  # 1 ,2 , 3, 4, 5, 6
                post_type = request_data.get('type', None)  # 11 , 12, 13, 14
                mahals = request_data.get('mahal', [])
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

                # Start with the base query and replace filter_by() with filter()
                query = Posts.query.filter(Posts.city == city)
                query = query.filter(Posts.status == 1)
                if post_type is not None:
                    query = query.filter(Posts.type == post_type)

                if mahals:
                    query = query.filter(Posts.mahal.in_(mahals))  # Filter by mahal list

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
                    'desck': post.desck[:30]
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
            return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403
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
        # Parse JSON body
        request_data = request.get_json()

        # Default values, can be overridden by JSON body
        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        user = Users.query.filter_by(phone=user_phone).first()
        check_accses = check_user_has_accses(user, 0)
        if check_accses:
            try:
                city = request_data.get('city', 1) # 1 ,2 , 3, 4, 5, 6
                post_type = request_data.get('type', None)  # 11 , 12, 13, 14
                mahals = request_data.get('mahal', [])
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

                # Start with the base query and replace filter_by() with filter()
                query = Posts.query.filter(Posts.city == city)
                query = query.filter(Posts.status == 1)
                if post_type is not None:
                    query = query.filter(Posts.type == post_type)

                if mahals:
                    query = query.filter(Posts.mahal.in_(mahals))  # Filter by mahal list

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
                    'date_created_persian':query.date_created_persian
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
            return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403
    except Exception as e:
        print(e)
        return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره امتحان کنید !', 'message': str(e)}), 500
