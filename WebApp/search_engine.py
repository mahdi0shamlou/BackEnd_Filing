from flask import request, Blueprint, jsonify
import datetime
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
#-------------
#------------- models
from models import users as Users
from models import db
#---------------


searchenign_bp = Blueprint('searchenign', __name__)


@searchenign_bp.route('/Search', methods=['POST'])
@jwt_required()
def searhc_file():
    data = request.form
    phone = data.get('phone')

