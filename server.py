""" web server for the webapp """

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from model import connect_to_db, db, User, Collection, Photo, Person, PersonPhoto
from helper import (
upload_file_to_s3,
get_photo_bytestring_from_s3,
convert_photo_byte_string_to_url,
create_rekognition_collection,
index_faces,
delete_rekognition_collection,
get_face_id_image_info_dict,
search_faces,
make_photos_urls_dict,
make_cropped_face_images_dict,
get_photo_width_height,
make_cropped_face_image,
get_bounding_box_info_from_dict
)
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from secret import bucket, APP_SECRET_KEY
from flask_debugtoolbar import DebugToolbarExtension



# ******DELETE THE LINE BELOW WHEN YOU ARE DONE*****
from helper import list_rekognition_collections, delete_rek_collection

""" SOMETHING TO CHANGE LATER!!!
"""


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = APP_SECRET_KEY
# Raise an error when an undefined variable is used in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route('/login')
def login():
    if 'username' in session:
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/login/validate')
def validate_login():
    check_username = request.args.get('username')
    check_password = request.args.get('password')

    user = User.query.filter(User.username == check_username).first()
    if user:
        if user.password == check_password:
            flash('Welcome back, {}. You are successfully logged in.'.format(user.username))
            session['username'] = user.username
            return redirect('/')
        else:
            flash('Your username and password did not match. Please try again.')
            return redirect('/login')
    else:
        flash('Looks like you are not registered. Please register to start facial recognizing your photos.')
        return redirect('/register')


@app.route('/register')
def register():
    if 'username' in session:
        return redirect('/')
    else:
        return render_template('register.html')


@app.route('/register/new_user', methods=['POST'])
def register_new_user():
    new_username = request.form.get('username')
    new_pwd = request.form.get('password')
    new_confirm_pwd = request.form.get('confirm_password')

    if new_username == '':
        flash('Please put in a username.')
        return redirect('/register')
    elif new_pwd == '':
        flash('Please put in a password.')
        return redirect('/register')
    elif new_confirm_pwd == '':
        flash('Please put in a confirm password.')
        return redirect('/register')

    all_users = User.query.all()
    for user in all_users:
        if user.username == new_username:
            flash('This username is already registered. Please register with another username or sign in.')
            return redirect('/register')

    if new_pwd != new_confirm_pwd:
        flash('The two passwords did not match. Please try again.')
        return redirect('/register')

    new_user = User(username=new_username, password=new_pwd)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = new_user.username
    flash('You have successfully registered, {}. You can start recognizing faces!'.format(new_user.username))

    return redirect('/')


@app.route('/logout')
def logout():
    del session['username']
    flash('You have successfully logged out.')
    return redirect('/login')


@app.route('/')
def index():
    """ Show the area for uploading pictures """
    if 'username' in session:
        return render_template('index.html')
    else:
        flash('Please log in to start recognizing faces.')
        return redirect('/login')


@app.route('/upload', methods=['POST'])
def upload():
    """ DOCS: http://zabana.me/notes/upload-files-amazon-s3-flask.html """

    files = request.files.getlist('user_file')
    user = User.query.filter(User.username == session['username']).first()

    # Check if there's a 'user_file' key
    if len(files) == 0:
        flash('No files were selected. Please select file(s) to upload.')
        return redirect('/')

    # Create a new collection instance and commit to database
    uuid_string = str(uuid.uuid4())
    new_collection = Collection(user=user, uuid=uuid_string)
    db.session.add(new_collection)
    db.session.commit()

    # Upload photos to s3
    try:
        upload_files(files, new_collection.id)
    except:
        flash('Failed to upload files. Please try again. ')
        return redirect('/')

    # Faces indexing and matching
    if create_rekognition_collection(new_collection.id) == True:
        try:
            for photo in new_collection.photos:
                index_faces(new_collection.id, photo.s3_key, photo.id)

            process_faces(new_collection.id)
        except:
            flash('Failed to process files. Please try again. ')
            return redirect('/')

    # Update the database with the time finish processing the collection
    new_collection.time_processed = datetime.utcnow()
    db.session.commit()

    flash('Your collection of pictures was processed successfully!')

    # Delete the collection when it's done
    delete_rekognition_collection(new_collection.id)

    return redirect(f'/collections/{new_collection.id}')


def upload_files(files, collection_id):
    # Go through each file, create a new Photo() and upload to S3
    for file in files:
        file.filename = secure_filename(file.filename)
        s3_key = upload_file_to_s3(file, bucket, collection_id)
        byte = get_photo_bytestring_from_s3(bucket, s3_key)
        (photo_width, photo_height) = get_photo_width_height(byte)
        db.session.add(Photo(
            collection_id=collection_id,
            s3_key=s3_key,
            byte_string=byte,
            width=photo_width,
            height=photo_height
        ))
    db.session.commit()


def process_faces(collection_id):
    photos_faces_dict = get_face_id_image_info_dict(collection_id)
    faces_list = photos_faces_dict.keys()
    # List to store the processed FaceId's
    processed_ids = []

    # Iterate through each FaceId and update the database
    for face in faces_list:
        if face not in processed_ids:
            # Match the FaceId with other faces
            # Get all the FaceId's that belong to the same person
            face_ids_of_same_person = search_faces(collection_id, face)
            person = Person(collection_id=collection_id)

            # Connect the person obejct with all its photo objects
            for matched_face in face_ids_of_same_person:
                matched_face_properties = photos_faces_dict[matched_face]
                photo = Photo.query.get(matched_face_properties['photo_id'])
                (face_width, face_height, face_top, face_left) = get_bounding_box_info_from_dict(matched_face_properties)

                photo_byte_string = photo.byte_string
                photo_width = photo.width
                photo_height = photo.height
                image_bytes = make_cropped_face_image(
                                photo_byte_string,
                                photo_width,
                                photo_height,
                                face_width,
                                face_height,
                                face_top,
                                face_left
                )

                person_photo = PersonPhoto(
                    person=person,
                    photo=photo,
                    face_width_percentage=face_width,
                    face_height_percentage=face_height,
                    face_top_percentage=face_top,
                    face_left_percentage=face_left,
                    cropped_face_image=image_bytes
                )

                person.person_photo.append(person_photo)

            db.session.add(person)
            processed_ids = processed_ids + face_ids_of_same_person


@app.route('/collections/<int:collection_id>')
def show_collections(collection_id):
    """ Show the people list and photo list of that collection """
    photo_list = Photo.query.filter(Photo.collection_id == collection_id).all()
    person_list = Person.query.filter(Person.collection_id == collection_id).all()

    cropped_face_images_dict = make_cropped_face_images_dict(person_list)
    url_dict = make_photos_urls_dict(photo_list)

    # Create face bounding boxes for each indexed face
    boundingbox_dict = {}
    for photo in photo_list:
        boundingbox_list = []
        for person in photo.persons:
            person_photo = PersonPhoto.query.filter(PersonPhoto.person == person, PersonPhoto.photo == photo).first()
            boundingbox_list.append({
                'person_photo_id': person_photo.id,
                'face_top_percentage': person_photo.face_top_percentage,
                'face_left_percentage': person_photo.face_left_percentage,
                'face_width_percentage': person_photo.face_width_percentage,
                'face_height_percentage': person_photo.face_height_percentage,
            })
        boundingbox_dict[photo.id] = boundingbox_list

    return render_template('collections.html',
                collection_id=collection_id,
                photos=photo_list,
                url_dict=url_dict,
                persons=person_list,
                cropped_faces_dict=cropped_face_images_dict,
                boundingbox_dict=boundingbox_dict
            )


@app.route('/persons', methods=['GET'])
def person_detail():
    """ Show the list of pictures that this person was in """
    person_ids = request.args.getlist('person_ids[]')
    persons = Person.query.filter(Person.id.in_(person_ids)).all()

    unique_photo_set = None
    for person in persons:
        if not unique_photo_set:
            unique_photo_set = set(person.photos)
        else:
            unique_photo_set = unique_photo_set.intersection(set(person.photos))

    collection = Collection.query.get(person.collection_id)
    all_persons_list = Person.query.filter(Person.collection == collection).all()

    cropped_face_image_dict = make_cropped_face_images_dict(all_persons_list)
    photo_url_dict = make_photos_urls_dict(unique_photo_set)
    unique_photo_ids = [photo.id for photo in unique_photo_set]

    photo_data = db.session.query(
        Photo.id,
        Person.id,
        PersonPhoto.face_top_percentage,
        PersonPhoto.face_left_percentage,
        PersonPhoto.face_width_percentage,
        PersonPhoto.face_height_percentage,
    ).join(
        PersonPhoto,
        Person,
    ).filter(
        Photo.id.in_(unique_photo_ids),
        Person.id.in_(person_ids),
    ).all()

    boundingbox_dict = {}
    for photo_id, person_id, face_top, face_left, face_width, face_height in photo_data:
        if photo_id not in boundingbox_dict:
            boundingbox_dict[photo_id] = []

        boundingbox_dict[photo_id].append({
            person_id: {
                'face_top_percentage': face_top,
                'face_left_percentage': face_left,
                'face_width_percentage': face_width,
                'face_height_percentage': face_height,
            }
        })

    return render_template('persons.html',
                collection_id=collection.id,
                person_list=persons,
                url_dict=photo_url_dict,
                cropped_face_image_dict=cropped_face_image_dict,
                boundingbox_dict=boundingbox_dict,
                all_persons_list=all_persons_list
            )


@app.route('/photos/<int:photo_id>')
def photo_detail(photo_id):
    """ Show the list of people who were in this picture """
    photo = Photo.query.get(photo_id)
    persons = photo.persons

    collection = Collection.query.get(photo.collection_id)
    all_persons_list = Person.query.filter(Person.collection == collection).all()

    # Generate a byte string for image
    url = convert_photo_byte_string_to_url(photo.byte_string)
    cropped_face_images_dict = make_cropped_face_images_dict(all_persons_list)

    return render_template('photos.html',
                url=url,
                collection_id=collection.id,
                persons=persons,
                photo=photo,
                cropped_faces_dict=cropped_face_images_dict,
                person_photo_list=photo.person_photo,
                all_persons_list=all_persons_list,
            )


@app.route('/collections')
def get_all_collections():
    """Get json of available collections. """
    user = User.query.filter(User.username == session['username']).first()
    collections = Collection.query.filter(Collection.user == user, Collection.time_processed != None).all()
    data = []
    for collection in collections:
        data.append({
            'id': collection.id,
            'numPhotos': len(collection.photos),
            'numPersons': len(collection.persons),
        })

    return jsonify(data)


@app.route('/edit_name', methods=['POST'])
def edit_name():
    """ Update person's name in the database """
    try:
        person_id = request.form['person_id']
        name = request.form['name']
        person = Person.query.get(person_id)
        person.name = name
        db.session.commit()

        return 'True'

    except:
        return 'False'


@app.route('/c/<string:collection_uuid>')
def show_collection_by_uuid(collection_uuid):
    return redirect('/')


if __name__ == '__main__':
    # Set app configurations
    # True to enable invoking the DebugToolbarExtension
    app.debug = True
    # Make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
