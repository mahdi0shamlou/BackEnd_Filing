from flask import request, Blueprint, jsonify
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
#-------------
#------------- models
from models import users as Users
from models import PostFileSell, PostFileRent
from sqlalchemy import or_
#---------------

searchenign_bp = Blueprint('searchenign', __name__)

def check_user_has_accses(user, mahal):
    print(user)
    print(mahal)
    return True


@searchenign_bp.route('/Search', methods=['POST'])
@jwt_required()
def search_engine():
    try:
        # Parse JSON body
        request_data = request.get_json()

        # Default values, can be overridden by JSON body
        is_sell = request_data.get('type_file', 1)
        if is_sell == 1:
            current_user = get_jwt_identity()
            user_phone = current_user['phone']

            user = Users.query.filter_by(phone=user_phone).first()
            check_accses = check_user_has_accses(user, 0)
            if check_accses:
                try:
                    city = request_data.get('city', 1)
                    post_type = request_data.get('type', 11)  # Renamed 'type' to 'post_type'
                    mahals = request_data.get('mahal', [])
                    price_from = request_data.get('price_from', None)
                    price_to = request_data.get('price_to', None)
                    meter_from = request_data.get('meter_from', None)
                    meter_to = request_data.get('meter_to', None)
                    sort_from = request_data.get('sort', 1)
                    page = request_data.get('page', 1)
                    otagh = request_data.get('otagh', None)
                    make = request_data.get('make', [])
                    desck = request_data.get('desck', None)

                    # Start with the base query and replace filter_by() with filter()
                    query = PostFileSell.query.filter(PostFileSell.city == city)
                    query = query.filter(PostFileSell.status == 1)
                    if post_type is not None:
                        query = query.filter(PostFileSell.type == post_type)

                    if mahals:
                        query = query.filter(PostFileSell.mahal.in_(mahals))  # Filter by mahal list

                    if price_from is not None and price_to is not None:
                        query = query.filter(PostFileSell.price.between(price_from, price_to))
                    elif price_from is not None:
                        query = query.filter(PostFileSell.price >= price_from)
                    elif price_to is not None:
                        query = query.filter(PostFileSell.price <= price_to)

                    if meter_from is not None and meter_to is not None:
                        query = query.filter(PostFileSell.meter.between(meter_from, meter_to))
                    elif meter_from is not None:
                        query = query.filter(PostFileSell.meter >= meter_from)
                    elif meter_to is not None:
                        query = query.filter(PostFileSell.meter <= meter_to)

                    if otagh is not None:
                        if otagh != -1:
                            query = query.filter(PostFileSell.Otagh == otagh)

                    if make:
                        if -1 not in make:
                            query = query.filter(PostFileSell.Make_years.in_(make[:4]))

                    if 'parking' in request_data:
                        query = query.filter(PostFileSell.PARKING == True)

                    if 'cabinet' in request_data:
                        query = query.filter(PostFileSell.CABINET == True)

                    if 'elevator' in request_data:
                        query = query.filter(PostFileSell.ELEVATOR == True)

                    if desck is not None:
                        query = query.filter(or_(
                            PostFileSell.desck.ilike(f'%{desck}%'),
                            PostFileSell.title.ilike(f'%{desck}%')
                        ))

                    per_page = 12


                    posts_pagination = query.order_by(PostFileSell.id.desc()).paginate(page=page, per_page=per_page,
                                                                                           error_out=False)

                    posts = posts_pagination.items

                    # Build a list of post details to send in the response
                    posts_list = [{
                        'type_file': is_sell,
                        'id': post.id,
                        'title': post.title,
                        'city': post.city_text,
                        'price': post.price,
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
        else:
            current_user = get_jwt_identity()
            user_phone = current_user['phone']

            user = Users.query.filter_by(phone=user_phone).first()
            check_accses = check_user_has_accses(user, 0)
            if check_accses:
                try:
                    city = request_data.get('city', 1)
                    post_type = request_data.get('type', 21)  # Renamed 'type' to 'post_type'
                    mahals = request_data.get('mahal', [])
                    price_from = request_data.get('price_from', None)
                    price_to = request_data.get('price_to', None)
                    rent_from = request_data.get('rent_from', None)
                    rent_to = request_data.get('rent_to', None)
                    meter_from = request_data.get('meter_from', None)
                    meter_to = request_data.get('meter_to', None)
                    page = request_data.get('page', 1)
                    otagh = request_data.get('otagh', None)
                    make = request_data.get('make', [])
                    desck = request_data.get('desck', None)

                    # Start with the base query and replace filter_by() with filter()
                    query = PostFileRent.query.filter(PostFileRent.city == city)
                    query = query.filter(PostFileRent.status == 1)

                    if post_type is not None:
                        query = query.filter(PostFileRent.type == post_type)

                    if mahals:
                        query = query.filter(PostFileRent.mahal.in_(mahals))  # Filter by mahal list

                    if price_from is not None and price_to is not None:
                        query = query.filter(PostFileRent.price.between(price_from, price_to))
                    elif price_from is not None:
                        query = query.filter(PostFileRent.price >= price_from)
                    elif price_to is not None:
                        query = query.filter(PostFileRent.price <= price_to)

                    if rent_from is not None and rent_to is not None:
                        query = query.filter(PostFileRent.rent.between(rent_from, rent_to))
                    elif rent_from is not None:
                        query = query.filter(PostFileRent.rent >= rent_from)
                    elif rent_to is not None:
                        query = query.filter(PostFileRent.rent <= rent_to)


                    if meter_from is not None and meter_to is not None:
                        query = query.filter(PostFileRent.meter.between(meter_from, meter_to))
                    elif meter_from is not None:
                        query = query.filter(PostFileRent.meter >= meter_from)
                    elif meter_to is not None:
                        query = query.filter(PostFileRent.meter <= meter_to)

                    if otagh is not None:
                        if otagh != -1:
                            query = query.filter(PostFileRent.Otagh == otagh)

                    if make:
                        if -1 not in make:
                            query = query.filter(PostFileRent.Make_years.in_(make[:4]))

                    if 'parking' in request_data:
                        query = query.filter(PostFileRent.PARKING == True)

                    if 'cabinet' in request_data:
                        query = query.filter(PostFileRent.CABINET == True)

                    if 'elevator' in request_data:
                        query = query.filter(PostFileRent.ELEVATOR == True)

                    if desck is not None:
                        query = query.filter(or_(
                            PostFileRent.desck.ilike(f'%{desck}%'),
                            PostFileRent.title.ilike(f'%{desck}%')
                        ))

                    per_page = 12

                    posts_pagination = query.order_by(PostFileRent.id.desc()).paginate(page=page, per_page=per_page,
                                                                                           error_out=False)

                    posts = posts_pagination.items

                    # Build a list of post details to send in the response
                    posts_list = [{
                        'type_file': is_sell,
                        'id': post.id,
                        'title': post.title,
                        'city': post.city_text,
                        'price': post.price,
                        'rent': post.rent,
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
