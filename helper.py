import boto3, botocore
import base64

from secret import bucket
import pprint

# for print pretty on API response objects
pp = pprint.PrettyPrinter(indent=4)

# Using s3
s3 = boto3.client('s3')
# Using Amazon rekognition
rekognition = boto3.client('rekognition')


""" SOMETHING TO CHANGE LATER!!!
2. error handling of upload_file_to_s3
3. hide bucket name"""


# helper function to upload files to Amazon S3
def upload_file_to_s3(file, bucket_name, collection_id, acl='private'):
    """ DOCS: http://zabana.me/notes/upload-files-amazon-s3-flask.html """
    key_name = 'collection{}/{}'.format(collection_id, file.filename)

    try:
        # uploading a file object to Amazon S3
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

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e

    return "{}".format(key_name)


def get_photo_bytestring_from_s3(bucket_name, key_name):

    # getting a file object from s3
    response = s3.get_object(Bucket=bucket_name, Key=key_name)
    # reading in the byte string from the response
    byte_string = response['Body'].read()

    return byte_string


def convert_photo_byte_string_to_url(byte_string):

    url = 'data:image/jpeg;base64,' + base64.b64encode(byte_string).decode('utf8')

    return url


def create_rekognition_collection(collection_id):
    # create a rekognition collection for a collection of photos to store indexed faces
    collection_name = 'collection{}'.format(collection_id)
    response = rekognition.create_collection(CollectionId=collection_name)
    # pp.pprint(response)


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
    # pp.pprint(response)

    # result = {}
    # result['ExternalImageId'] = response['FaceRecords']


def delete_rekognition_collection(collection_id):

    collection_name = 'collection{}'.format(collection_id)
    response = rekognition.delete_collection(CollectionId=collection_name)
    # pp.pprint(response)


def get_faceId_externalImageId_dict(collection_id):

    collection_name = 'collection{}'.format(collection_id)
    response = rekognition.list_faces(CollectionId=collection_name)
    pp.pprint(response)
    # faces_list = []

    faceId_externalImageId_dict = {}

    for face in response['Faces']:
        faceId_externalImageId_dict[face['FaceId']] = {'photo_id': face['ExternalImageId'], 'BoundingBox': face['BoundingBox']}

    pp.pprint(faceId_externalImageId_dict)

    return faceId_externalImageId_dict


def search_faces(collection_id, face_id):

    collection_name = 'collection{}'.format(collection_id)
    response = rekognition.search_faces(
        CollectionId=collection_name,
        FaceId=face_id,
        MaxFaces=123,
        FaceMatchThreshold=75.0
    )

    # pp.pprint(response)

    matched_faces_list = [face_id]
    if response['FaceMatches']:
        for matched_face in response['FaceMatches']:
            matched_faces_list.append(matched_face['Face']['FaceId'])

    return matched_faces_list


def make_photos_urls_dict(photo_list):

    url_dict={}
    for photo in photo_list:
        url_dict[photo.id] = convert_photo_byte_string_to_url(photo.byte_string)

    return url_dict

# ********DELETE EVERYTHING BELOW WHEN YOU ARE DONE*********

def list_rekognition_collections():
    response = rekognition.list_collections()
    print(response)


def delete_rek_collection(collection_name):

    response = rekognition.delete_collection(CollectionId=collection_name)


