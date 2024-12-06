from models import db
from models import Classification, ClassificationNeighborhood, Neighborhood, UserAccess
from flask import Blueprint, jsonify, make_response
from sqlalchemy import select


test_bp = Blueprint('test', __name__)


def get_user_neighborhoods_access_2(user_id):
    try:
        # ساخت کوئری با select
        user_classifications = select(UserAccess.classifictions_id).where(
            UserAccess.user_id == user_id
        ).scalar_subquery()

        # کوئری اصلی
        neighborhoods = db.session.query(
            Neighborhood.name,
            Classification.name.label('classification_name'),
            ClassificationNeighborhood.type
        ).join(
            ClassificationNeighborhood,
            Neighborhood.id == ClassificationNeighborhood.neighborhood_id
        ).join(
            Classification,
            ClassificationNeighborhood.classifiction_id == Classification.id
        ).filter(
            Classification.id.in_(user_classifications)
        ).all()

        # تبدیل نتایج به دیکشنری
        result = []
        for n in neighborhoods:
            result.append({
                'neighborhood_name': n.name,
                'classification_name': n.classification_name,
                'access_type': n.type
            })
        return result

    except Exception as e:
        print(f"Error in get_user_neighborhoods_access_2: {str(e)}")
        return None


@test_bp.route('/test/<int:user_id>', methods=['GET'])
def tests(user_id):
    try:
        results = get_user_neighborhoods_access_2(user_id)
        print(results)

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
