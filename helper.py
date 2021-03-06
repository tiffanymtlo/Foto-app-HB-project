import boto3, botocore
import base64
from PIL import Image, ImageDraw
import io
from secret import bucket

# Using s3 and rekognition
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')


# Upload files to Amazon S3
def upload_file_to_s3(file, bucket_name, collection_id, acl='private'):
    """ DOCS: http://zabana.me/notes/upload-files-amazon-s3-flask.html """
    key_name = 'collection{}/{}'.format(collection_id, file.filename)

    """ setting Content_Type allows users to read the file rather than
        to prompt users to download the files """
    s3.upload_fileobj(
        file,
        bucket_name,
        key_name,
        ExtraArgs={
            "ACL": acl,
            "ContentType": file.content_type
        }
    )

    return "{}".format(key_name)


def get_photo_bytestring_from_s3(bucket_name, key_name):
    # Get the file object from s3 and return its byte string
    response = s3.get_object(Bucket=bucket_name, Key=key_name)

    return response['Body'].read()


def convert_photo_byte_string_to_url(byte_string):
    return 'data:image/jpeg;base64,' + base64.b64encode(byte_string).decode('utf8')


def create_rekognition_collection(collection_id):
    # Create a rekognition collection to store indexed faces
    try:
        collection_name = 'collection{}'.format(collection_id)
        response = rekognition.create_collection(CollectionId=collection_name)
        return True
    except:
        return False


def index_faces(collection_id, path, photo_id):
    collection_name = 'collection{}'.format(collection_id)

    response = rekognition.index_faces(
        CollectionId=collection_name,
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': path,
            }
        },
        ExternalImageId=str(photo_id),
        DetectionAttributes=[
            'DEFAULT'
        ],
        MaxFaces=50,
        QualityFilter='AUTO'
    )


def delete_rekognition_collection(collection_id):
    collection_name = 'collection{}'.format(collection_id)
    response = rekognition.delete_collection(CollectionId=collection_name)


def get_face_id_image_info_dict(collection_id):
    collection_name = 'collection{}'.format(collection_id)
    response = rekognition.list_faces(CollectionId=collection_name)
    result = {}

    for face in response['Faces']:
        result[face['FaceId']] = {
            'photo_id': face['ExternalImageId'],
            'bounding_box': face['BoundingBox'],
        }

    return result


def search_faces(collection_id, face_id):
    collection_name = 'collection{}'.format(collection_id)
    response = rekognition.search_faces(
        CollectionId=collection_name,
        FaceId=face_id,
        MaxFaces=123,
        FaceMatchThreshold=90.0
    )

    same_person_face_ids = [
        face["Face"]["FaceId"] for face in response["FaceMatches"]
    ]
    same_person_face_ids.append(face_id)

    return same_person_face_ids


def make_photos_urls_dict(photo_list):
    url_dict={}
    for photo in photo_list:
        url_dict[photo.id] = convert_photo_byte_string_to_url(photo.byte_string)

    return url_dict


def get_photo_width_height(byte):
    image = Image.open(io.BytesIO(byte))
    width, height = image.size
    image.close()

    return (width, height)


def get_bounding_box_info_from_dict(info_dict):
    face_width_percentage = info_dict['bounding_box']['Width']
    face_height_percentage = info_dict['bounding_box']['Height']
    face_top_percentage = info_dict['bounding_box']['Top']
    face_left_percentage = info_dict['bounding_box']['Left']

    return (face_width_percentage, face_height_percentage, face_top_percentage, face_left_percentage)


def make_cropped_face_image(photo_byte_string, photo_width, photo_height, face_width_percentage, face_height_percentage, face_top_percentage, face_left_percentage):
    image = Image.open(io.BytesIO(photo_byte_string))
    buffer = 15
    left = face_left_percentage * photo_width - buffer
    top = face_top_percentage * photo_height - buffer
    right = (face_width_percentage * photo_width) + (face_left_percentage * photo_width) + buffer
    bottom = (face_height_percentage * photo_height) + (face_top_percentage * photo_height) + buffer
    cropped_image = image.crop((left, top, right, bottom))
    byte_string = io.BytesIO()
    cropped_image.save(byte_string, format='PNG')
    image_bytes = byte_string.getvalue()
    image.close()

    return image_bytes


def make_cropped_face_images_dict(persons_list):
    result={}
    for person in persons_list:
        persons_photos_list = person.person_photo
        if len(persons_photos_list):
            result[person.id] = convert_photo_byte_string_to_url(persons_photos_list[0].cropped_face_image)

    return result

# ********DELETE EVERYTHING BELOW WHEN YOU ARE DONE*********

def list_rekognition_collections():
    response = rekognition.list_collections()
    print(response)


def delete_rek_collection(collection_name):

    response = rekognition.delete_collection(CollectionId=collection_name)
