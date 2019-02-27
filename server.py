""" web server for the webapp """

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from model import connect_to_db, db, Collection, Photo, Person, PersonPhoto
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

@app.route('/')
def index():
    """ Show the area for uploading pictures """
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """ DOCS: http://zabana.me/notes/upload-files-amazon-s3-flask.html """

    files = request.files.getlist('user_file')

    # Check if there's a 'user_file' key
    if len(files) == 0:
        flash('No files were selected. Please select file(s) to upload.')
        return redirect('/')

    # Create a new collection instance and commit to database
    new_collection = Collection()
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
    persons = request.args.getlist('persons[]')

    photo_set_list = []
    person_list = []
    for person_id in persons:
        person = Person.query.get(person_id)
        photo_list = person.photos
        photo_set = set(photo_list)
        photo_set_list.append(photo_set)
        person_list.append(person)

    unique_photo_set = photo_set_list.pop()
    while(len(photo_set_list) > 0):
        current_photo_set = photo_set_list.pop()
        unique_photo_set = unique_photo_set.intersection(current_photo_set)

    cropped_face_image_dict = make_cropped_face_images_dict(person_list)
    photo_url_dict = make_photos_urls_dict(unique_photo_set)

    boundingbox_dict = {}
    for photo in unique_photo_set:
        person_bounding_boxes_list = []
        for person in person_list:
            person_photo = PersonPhoto.query.filter(PersonPhoto.person == person, PersonPhoto.photo == photo).first()
            person_bounding_boxes_list.append({
                    person.id: {
                            'face_top_percentage': person_photo.face_top_percentage,
                            'face_left_percentage': person_photo.face_left_percentage,
                            'face_width_percentage': person_photo.face_width_percentage,
                            'face_height_percentage': person_photo.face_height_percentage
                    }
            })

        boundingbox_dict[photo.id] = person_bounding_boxes_list

    return render_template('persons.html',
                collection_id=person.collection_id,
                person_list=person_list,
                url_dict=photo_url_dict,
                cropped_face_image_dict=cropped_face_image_dict,
                boundingbox_dict=boundingbox_dict
            )




    # person = Person.query.get(person_id)
    # photo_list = person.photos
    #
    # cropped_face_image = convert_photo_byte_string_to_url(person.person_photo[0].cropped_face_image)
    # photo_url_dict = make_photos_urls_dict(photo_list)
    #
    # boundingbox_dict = {}
    # for photo in photo_list:
    #     person_photo = PersonPhoto.query.filter(PersonPhoto.person == person, PersonPhoto.photo == photo).first()
    #     boundingbox_dict[photo.id] = {
    #             'face_top_percentage': person_photo.face_top_percentage,
    #             'face_left_percentage': person_photo.face_left_percentage,
    #             'face_width_percentage': person_photo.face_width_percentage,
    #             'face_height_percentage': person_photo.face_height_percentage
    #     }
    #
    # return render_template('persons.html',
    #             collection_id=person.collection_id,
    #             person=person,
    #             url_dict=photo_url_dict,
    #             cropped_face_image=cropped_face_image,
    #             boundingbox_dict=boundingbox_dict
    #         )






# @app.route('/persons/<int:person_id>')
# def person_detail(person_id):
#     """ Show the list of pictures that this person was in """
#     person = Person.query.get(person_id)
#     photo_list = person.photos
#
#     cropped_face_image = convert_photo_byte_string_to_url(person.person_photo[0].cropped_face_image)
#     photo_url_dict = make_photos_urls_dict(photo_list)
#
#     boundingbox_dict = {}
#     for photo in photo_list:
#         person_photo = PersonPhoto.query.filter(PersonPhoto.person == person, PersonPhoto.photo == photo).first()
#         boundingbox_dict[photo.id] = {
#                 'face_top_percentage': person_photo.face_top_percentage,
#                 'face_left_percentage': person_photo.face_left_percentage,
#                 'face_width_percentage': person_photo.face_width_percentage,
#                 'face_height_percentage': person_photo.face_height_percentage
#         }
#
#     return render_template('persons.html',
#                 collection_id=person.collection_id,
#                 person=person,
#                 url_dict=photo_url_dict,
#                 cropped_face_image=cropped_face_image,
#                 boundingbox_dict=boundingbox_dict
#             )


@app.route('/photos/<int:photo_id>')
def photo_detail(photo_id):
    """ Show the list of people who were in this picture """
    photo = Photo.query.get(photo_id)
    persons = photo.persons

    # Generate a byte string for image
    url = convert_photo_byte_string_to_url(photo.byte_string)
    cropped_face_images_dict = make_cropped_face_images_dict(persons)

    return render_template('photos.html',
                url=url,
                collection_id=photo.collection_id,
                persons=persons,
                photo=photo,
                cropped_faces_dict=cropped_face_images_dict,
                person_photo_list=photo.person_photo
            )


@app.route('/collections')
def get_all_collections():
    """Get json of available collections. """
    collections = Collection.query.all()
    data = []
    for collection in collections:
        data.append({
            'id': collection.id,
            'numPhotos': len(collection.photos),
            'numPersons': len(collection.persons),
        })

    return jsonify(data)


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
