from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import TINYINT
import datetime

db = SQLAlchemy()

class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(191), unique=True, nullable=False)
    password = db.Column(db.String(191), nullable=False)
    name = db.Column(db.String(191), nullable=False)
    phone = db.Column(db.String(191), nullable=False)
    address = db.Column(db.Text)
    email = db.Column(db.String(191), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.now())

class Posts(db.Model):
    __tablename__ = 'Posts'
    #----------------- start
    # general details
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(191), unique=True, nullable=False)
    # number
    number = db.Column(db.String(191), nullable=False)
    # location details
    city = db.Column(db.BigInteger, nullable=False)
    city_text = db.Column(db.String(191), nullable=False)
    mahal = db.Column(db.BigInteger, nullable=False)
    mahal_text = db.Column(db.String(191), nullable=False)
    map = db.Column(db.Text)
    # type
    type = db.Column(db.BigInteger, nullable=False)
    # title and desck and images
    title = db.Column(db.String(191), nullable=False)
    desck = db.Column(db.Text)
    Images = db.Column(db.Text)
    # more details
    price = db.Column(db.BigInteger, nullable=False)
    price_per_meter = db.Column(db.BigInteger, nullable=False)
    meter = db.Column(db.BigInteger, nullable=False)
    Otagh = db.Column(TINYINT(unsigned=True))
    Make_years = db.Column(db.BigInteger)
    # true false details
    PARKING = db.Column(db.Boolean, default=False)
    ELEVATOR = db.Column(db.Boolean, default=False)
    CABINET = db.Column(db.Boolean, default=False)
    BALCONY = db.Column(db.Boolean, default=False)
    # dict data
    details = db.Column(db.Text)
    # date
    date_created_persian = db.Column(db.String(20))
    date_created = db.Column(db.DateTime, default= datetime.datetime.now())  # Use datetime.utcnow for default value


"""
class PostFileSell(db.Model):
    __tablename__ = 'PostFileSell'
    #----------------- start
    # general details
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(191), unique=True, nullable=False)
    # number
    number = db.Column(db.String(191), nullable=False)
    # location details
    city = db.Column(db.BigInteger, nullable=False)
    city_text = db.Column(db.String(191), nullable=False)
    mahal = db.Column(db.BigInteger, nullable=False)
    mahal_text = db.Column(db.String(191), nullable=False)
    map = db.Column(db.Text)
    # type
    type = db.Column(db.BigInteger, nullable=False)
    # title and desck and images
    title = db.Column(db.String(191), nullable=False)
    desck = db.Column(db.Text)
    Images = db.Column(db.Text)
    # more details
    price = db.Column(db.BigInteger, nullable=False)
    price_per_meter = db.Column(db.BigInteger, nullable=False)
    meter = db.Column(db.BigInteger, nullable=False)
    Otagh = db.Column(TINYINT(unsigned=True))
    Make_years = db.Column(db.BigInteger)
    # true false details
    PARKING = db.Column(db.Boolean, default=False)
    ELEVATOR = db.Column(db.Boolean, default=False)
    CABINET = db.Column(db.Boolean, default=False)
    BALCONY = db.Column(db.Boolean, default=False)
    # dict data
    details = db.Column(db.Text)
    # date
    date_created_persian = db.Column(db.String(20))
    date_created = db.Column(db.DateTime, default= datetime.datetime.now())  # Use datetime.utcnow for default value

class PostFileRent(db.Model):
    __tablename__ = 'PostFileRent'
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(191), unique=True, nullable=False)
    number = db.Column(db.String(191), nullable=False)
    city = db.Column(db.BigInteger, nullable=False)
    city_text = db.Column(db.String(191), nullable=False)
    mahal = db.Column(db.BigInteger, nullable=False)
    mahal_text = db.Column(db.String(191), nullable=False)
    type = db.Column(db.BigInteger, nullable=False)
    title = db.Column(db.String(191), nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    rent = db.Column(db.BigInteger, nullable=False)
    meter = db.Column(db.BigInteger, nullable=False)
    desck = db.Column(db.Text)
    map = db.Column(db.Text)
    Images = db.Column(db.Text)
    Otagh = db.Column(TINYINT(unsigned=True))
    Make_years = db.Column(db.BigInteger)
    # True and False details
    PARKING = db.Column(db.Boolean, default=False)
    ELEVATOR = db.Column(db.Boolean, default=False)
    CABINET = db.Column(db.Boolean, default=False)
    BALCONY = db.Column(db.Boolean, default=False)
    # dict data
    details = db.Column(db.Text)
    #date
    date_created_persian = db.Column(db.String(20))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())  # Use datetime.utcnow for default value


class Notes(db.Model):
    __tablename__ = 'Notes'
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.Integer, nullable=False)
"""

