import boto3
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

# Let's use Amazon S3
s3 = boto3.resource('s3')

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)
#     bucket_name = bucket.name

# file_name = 'location-of-your-file'
# key_name = 'name-of-file-in-s3'
# s3.upload_file(file_name, bucket_name, key_name)


# conversion to a list
buckets = list(s3.buckets.all())
print(buckets)



if __name__ == "__main__":


    collectionId='zuck1'
    photo1='zuck1.jpg'
    photo2='zuck2.jpg'
    bucket='hbprojecttest'
    
    client=boto3.client('rekognition')

    # # #Create a collection
    # print('Creating collection:' + collectionId)
    # response_create_collection = client.create_collection(CollectionId=collectionId)
    # print(response_create_collection)
    # print('Collection ARN: ' + response_create_collection['CollectionArn'])
    # print('Status code: ' + str(response_create_collection['StatusCode']))
    # print('Done...')


    # # index faces
    response_index_faces = client.index_faces(
        CollectionId=collectionId,
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': 'collection4/zuck1.jpg',
            }
        },
        ExternalImageId='zuck1.jpg',
        DetectionAttributes=[
            'ALL'
        ],
        MaxFaces=123,
        QualityFilter='AUTO'
    )

    # pp.pprint(response_index_faces)

    # # describe the collection
    # response_describe_collection = client.describe_collection(
    #     CollectionId=collectionId
    # )
    # pp.pprint(response_describe_collection)


    # # index faces for second pic
    # response_index_faces_2 = client.index_faces(
    #     CollectionId=collectionId,
    #     Image={
    #         'S3Object': {
    #             'Bucket': bucket,
    #             'Name': photo2,
    #         }
    #     },
    #     ExternalImageId=photo2,
    #     DetectionAttributes=[
    #         'ALL'
    #     ],
    #     MaxFaces=123,
    #     QualityFilter='AUTO'
    # )

    # pp.pprint(response_index_faces_2)


    # # describe the collection
    # response_describe_collection2 = client.describe_collection(
    #     CollectionId=collectionId
    # )
    # pp.pprint(response_describe_collection2)

    # list faces in a collection
    response_list_faces = client.list_faces(
        CollectionId=collectionId
    )

    pp.pprint(response_list_faces)


    # search a face in photo1
    response_search_faces_1 = client.search_faces(
        CollectionId=collectionId,
        FaceId=response_list_faces['Faces'][2]['FaceId'],
        MaxFaces=123,
        FaceMatchThreshold=80.0
    )

    pp.pprint(response_search_faces_1)





