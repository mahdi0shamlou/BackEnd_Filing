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
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    zoonkans = relationship('ZoonKan', back_populates='user', cascade='all, delete-orphan')
    files_in_zoonkan = relationship('FilesInZoonKan', back_populates='user', cascade='all, delete-orphan')

    user_access = relationship('UserAccess', back_populates='user', cascade='all, delete-orphan')

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
    date_created = db.Column(db.DateTime, default= datetime.now())  # Use datetime.utcnow for default value
    files_in_zoonkan = relationship('FilesInZoonKan', back_populates='post', cascade='all, delete-orphan')

class Notes(db.Model):
    __tablename__ = 'Notes'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id_created = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    file_id_created = db.Column(db.BigInteger, db.ForeignKey('Posts.id', ondelete='CASCADE'), nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

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

class Classification(db.Model):
    __tablename__ = 'Classifictions'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(191), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    neighborhoods = relationship('ClassificationNeighborhood', back_populates='classification')
    user_access = relationship('UserAccess', back_populates='classification')

class ClassificationNeighborhood(db.Model):
    __tablename__ = 'Classifictions_Neighborhoods'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    classifiction_id = db.Column(db.BigInteger, db.ForeignKey('Classifictions.id', ondelete='CASCADE'), nullable=False)
    neighborhood_id = db.Column(db.BigInteger, db.ForeignKey('Neighborhoods.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    classification = relationship('Classification', back_populates='neighborhoods')
    neighborhood = relationship('Neighborhood', back_populates='classifications')

class ClassificationTypes(db.Model):
    __tablename__ = 'Classifictions_Types'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    classifiction_id = db.Column(db.BigInteger, db.ForeignKey('Classifictions.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

class Types_file(db.Model):
    __tablename__ = 'Types_file'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(191), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

class Factor(db.Model):
    __tablename__ = 'Factors'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    expired_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

class FactorAccess(db.Model):
    __tablename__ = 'Factor_Access'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    factor_id = db.Column(db.BigInteger, db.ForeignKey('Factors.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    classifictions_id = db.Column(db.BigInteger, db.ForeignKey('Classifictions.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    expired_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

class UserAccess(db.Model):
    __tablename__ = 'User_Access'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    factor_id = db.Column(db.BigInteger, db.ForeignKey('Factors.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    classifictions_id = db.Column(db.BigInteger, db.ForeignKey('Classifictions.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    expired_at = db.Column(db.DateTime, nullable=False)

    user = relationship('users', back_populates='user_access')  # حذف backref و استفاده از back_populates
    classification = relationship('Classification', back_populates='user_access')

class Neighborhood(db.Model):
    __tablename__ = 'Neighborhoods'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(191), nullable=False)
    city_id = db.Column(db.BigInteger, db.ForeignKey('Cities.id', ondelete='CASCADE'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    classifications = relationship('ClassificationNeighborhood', back_populates='neighborhood')
