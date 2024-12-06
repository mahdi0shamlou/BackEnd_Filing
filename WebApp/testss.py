from models import users as User
from models import db
from models import Classification, ClassificationNeighborhood, Neighborhood, UserAccess
from flask import Blueprint, jsonify

test_bp = Blueprint('test', __name__)


# روش 1: استفاده از join های متوالی
def get_user_neighborhoods_access_1(user_id):
    neighborhoods = db.session.query(
        User.name.label('user_name'),
        Classification.name.label('classification_name'),
        Neighborhood.name.label('neighborhood_name'),
        ClassificationNeighborhood.type
    ).join(
        UserAccess, User.id == UserAccess.user_id
    ).join(
        Classification, UserAccess.classifictions_id == Classification.id
    ).join(
        ClassificationNeighborhood, Classification.id == ClassificationNeighborhood.classifiction_id
    ).join(
        Neighborhood, ClassificationNeighborhood.neighborhood_id == Neighborhood.id
    ).filter(
        User.id == user_id
    ).all()

    return neighborhoods

@test_bp.route('/test', methods=['POST'])
def tests():
    x = get_user_neighborhoods_access_1(2)
    return jsonify({'message': str(x)}), 200
