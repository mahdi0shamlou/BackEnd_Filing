from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import TINYINT
from datetime import datetime
from sqlalchemy.orm import relationship



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
    zoonkans = relationship('ZoonKan', back_populates='user', cascade='all, delete-orphan')
    files_in_zoonkan = relationship('FilesInZoonKan', back_populates='user', cascade='all, delete-orphan')

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
    type_text = db.Column(db.String(191), nullable=False)
    # title and desck and images
    title = db.Column(db.String(191), nullable=False)
    desck = db.Column(db.Text)
    Images = db.Column(db.Text)
    # more details
    price = db.Column(db.BigInteger, nullable=False)
    price_two = db.Column(db.BigInteger, nullable=False)
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
    files_in_zoonkan = relationship('FilesInZoonKan', back_populates='post', cascade='all, delete-orphan')

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

class Notes(db.Model):
    __tablename__ = 'Notes'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id_created = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    file_id_created = db.Column(db.BigInteger, db.ForeignKey('Posts.id', ondelete='CASCADE'), nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.now())


class ZoonKan(db.Model):
    __tablename__ = 'ZoonKan'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id_created = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(191), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    # Relationships
    user = relationship('users', back_populates='zoonkans')
    files = relationship('FilesInZoonKan', back_populates='zoonkan', cascade='all, delete-orphan')


class FilesInZoonKan(db.Model):
    __tablename__ = 'FilesInZoonKan'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id_created = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    file_id_created = db.Column(db.BigInteger, db.ForeignKey('Posts.id', ondelete='CASCADE'), nullable=False)
    zoonkan_id_in = db.Column(db.BigInteger, db.ForeignKey('ZoonKan.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    # Relationships
    user = relationship('users', back_populates='files_in_zoonkan')
    post = relationship('Posts', back_populates='files_in_zoonkan')
    zoonkan = relationship('ZoonKan', back_populates='files')
