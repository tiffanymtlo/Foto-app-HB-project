""" web server for the webapp """

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db

# importing helper functions from helper.py
from helper import upload_file_to_s3, get_photo_bytestring_from_s3, convert_photo_byte_string_to_url, create_rekognition_collection, index_faces, delete_rekognition_collection, get_externalImageId_faceId_dict, search_faces
# importing werkzeug for later use
from werkzeug.utils import secure_filename

# from secret import bucket, collection
from model import Collection, Photo, Person, PersonPhoto

from datetime import datetime
from secret import bucket, APP_SECRET_KEY


""" SOMETHING TO CHANGE LATER!!!
1. bucket value (need to be dynamic)
2. error handling for upload_file_to_s3
"""


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = APP_SECRET_KEY

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def upload():
    """ Show the area for uploading pictures """
    """ FIX THE HTML LATER """
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_pics_to_s3():

    """ DOCS: http://zabana.me/notes/upload-files-amazon-s3-flask.html """

    # Check if there's a 'user_file' key
    if len(request.files) <= 0:
        flash('No files were selected. Please select file(s) to upload.')
        return redirect('/')

    # Store the file object from request.files
    files = request.files.getlist("user_file")

    # # Check if there's a file
    if len(files):
    # if file and allowed_file(file.filename):

        # create a new collection instance and commit to database
        new_collection = Collection()
        db.session.add(new_collection)
        db.session.commit()

        # iterate through each file object in the files list of file objects
        for file in files:
            # get a secure version of filename
            file.filename = secure_filename(file.filename)
            # upload pic to s3
            output = upload_file_to_s3(file, bucket, new_collection.id)
            # save the path of the file uploaded as string
            path = str(output)

            # get the byte string representation of the image
            byte = get_photo_bytestring_from_s3(bucket, path)

            # create new Photo object for the file object
            new_photo = Photo(collection_id=new_collection.id, s3_key=path, byte_string=byte)
            db.session.add(new_photo)

        db.session.commit()

        flash('Your collection of pictures was uploaded successfully!')

        return redirect(f'/collections/{new_collection.id}')


@app.route('/collections/<int:collection_id>')
def show_collections(collection_id):
    """ Show the people list and photo list of that collection """
    """ FIX THE HTML LATER """
    """ maybe able to JUST PAST THE URL_LIST (No need the photo_list) """
    photo_list = Photo.query.filter(Photo.collection_id == collection_id).all()

    # delete_rekognition_collection(collection_id)
    create_rekognition_collection(collection_id)

    url_dict = {}

    for photo in photo_list:
        url_dict[photo.id] = convert_photo_byte_string_to_url(photo.byte_string)
        index_faces(collection_id, photo.s3_key, photo.id)

    photos_faces_dict = get_externalImageId_faceId_dict(collection_id)

    faces_list = []
    for faceId in photos_faces_dict:
        faces_list.append(faceId)

    # print(faces_list)
    processed_ids = []
    for face in faces_list:
        if face not in processed_ids:
            matched_faces = search_faces(collection_id, face)
            print(matched_faces)
            person = Person(collection_id=collection_id)
            print(person)
            for matched_face in matched_faces:
                photo = Photo.query.get(photos_faces_dict[matched_face])
                print(photo)
                person.photos.append(photo)
            db.session.add(person)
            db.session.commit()
            processed_ids = processed_ids + matched_faces

    delete_rekognition_collection(collection_id)

    return render_template('collections.html', collection_id=collection_id, photos=photo_list, url_dict=url_dict)


@app.route('/persons/1')
def person_detail():
    """ Show the list of pictures that this person was in """
    """ FIX THE HTML LATER """
    return render_template('persons.html')


@app.route('/photos/<int:photo_id>')
def photo_detail(photo_id):
    """ Show the list of people who were in this picture """
    """ FIX THE HTML LATER """
    photo = Photo.query.get(photo_id)
    collection_id = photo.collection_id

    # generate a byte array for the image to display
    url = convert_photo_byte_string_to_url(photo.byte_string)

    return render_template('photos.html', url=url, collection_id=collection_id)



if __name__ == '__main__':
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')