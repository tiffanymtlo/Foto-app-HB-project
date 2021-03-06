""" Models and database functions for the webapp """

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

database_name = 'photos_identify'

##############################################################################
# Model definitions

class User(db.Model):
    """ Users table """

    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    collections = db.relationship('Collection', backref='user')

    def __repr__(self):
        """ Print a helpful representation of the object """

        return f"""<User id={self.id}, username={self.username}>"""

class Collection(db.Model):
    """ Collections table """

    __tablename__ = 'collections'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_processed = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uuid = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"""<Collection id={self.id}, time_created={self.time_created}>"""


class Photo(db.Model):
    """ Photos table """

    __tablename__ = 'photos'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=False)
    s3_key = db.Column(db.String(200), nullable=False)
    byte_string = db.Column(db.LargeBinary, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)

    collection = db.relationship('Collection', backref='photos')
    persons = db.relationship('Person', secondary='persons_photos', backref='photos')
    person_photo = db.relationship('PersonPhoto', backref='photo')

    def __repr__(self):
        return f"""<Photo id={self.id}, collection_id={self.collection_id}, s3_key={self.s3_key}>"""


class Person(db.Model):
    """ Persons table """

    __tablename__ = 'persons'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=False)

    collection = db.relationship('Collection', backref='persons')
    person_photo = db.relationship('PersonPhoto', backref='person')
    uniqueids_persons = db.relationship('UniqueidPerson', backref='person')

    def __repr__(self):
        return f"""<Person id={self.id}, name={self.name}, collection_id={self.collection_id}>"""


class PersonPhoto(db.Model):
    """ Composite table between Photos and Persons tables """

    __tablename__ = 'persons_photos'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('persons.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=False)
    face_width_percentage = db.Column(db.Float, nullable=False)
    face_height_percentage = db.Column(db.Float, nullable=False)
    face_top_percentage = db.Column(db.Float, nullable=False)
    face_left_percentage = db.Column(db.Float, nullable=False)
    cropped_face_image = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return f"""<PersonPhoto id={self.id}, person_id={self.person_id}, photo_id={self.photo_id}, face_width_percentage={self.face_width_percentage}, face_height_percentage={self.face_height_percentage}, face_top_percentage={self.face_top_percentage}, face_left_percentage={self.face_left_percentage}>"""


class UniqueId(db.Model):
    """ Unique links table """

    __tablename__ = 'uniqueids'

    id = db.Column(db.Integer, autoincrement=True, primary_key = True)
    uuid = db.Column(db.String(200), nullable=False)

    persons = db.relationship('Person', secondary='uniqueids_persons', backref='uuids')
    uniqueids_persons = db.relationship('UniqueidPerson', backref='uuid')

    def __repr__(self):
        return f"""<UniqueID id={self.id}, uuid={self.uuid}>"""


class UniqueidPerson(db.Model):
        """ Composite table between UniqueId and Person tables """

        __tablename__ = 'uniqueids_persons'

        id = db.Column(db.Integer, autoincrement=True, primary_key=True)
        uuid_id = db.Column(db.Integer, db.ForeignKey('uniqueids.id'), nullable=False)
        person_id = db.Column(db.Integer, db.ForeignKey('persons.id'), nullable=False)

        def __repr__(self):
            return f"""<UniqueidPerson id={self.id}, uuid_id={self.uuid_id}, person_id={self.person_id}>"""


##############################################################################
# Helper functions

def connect_to_db(app, database_link='postgresql:///photos_identify'):
    """Connect the database to the Flask app."""

    # Configure to use database
    # Use photos_identify database if no database gets passed in
    app.config['SQLALCHEMY_DATABASE_URI'] = database_link
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if this module is run interactively, it will leave
    # in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    db.create_all()
    print("Connected to DB.")
