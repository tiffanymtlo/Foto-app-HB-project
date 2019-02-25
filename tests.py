import unittest
import server
from model import Collection, Photo, Person, PersonPhoto, connect_to_db, db, example_data
from server import app
from helper import (
    upload_file_to_s3,
    get_photo_bytestring_from_s3,
    get_photo_width_height,
    create_rekognition_collection,
    index_faces,
    get_face_id_external_image_id_dict,
    search_faces,
    get_bounding_box_info_from_dict,
    make_cropped_face_image,
    delete_rekognition_collection,
)
import io

class MockFlaskTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, 'postgresql:///testdb')

        # Create tables and add sample data
        db.create_all()
        # example_data()

        def _mock_upload_file_to_s3(file, bucket_name, collection_id, acl='private'):
            return 'collection1/photo1.jpg'

        def _mock_get_photo_bytestring_from_s3(bucket_name, key_name):
            return b'abcde'

        def _mock_get_photo_width_height(byte):
            return (123, 456)

        def _mock_create_rekognition_collection(collection_id):
            return True

        def _mock_index_faces(collection_id, path, photo_id):
            return None

        def _mock_get_face_id_external_image_id_dict(collection_id):
            result = {
                '48930575-3ea5': {
                    'bounding_box': {
                        'Height': 0.33,
                        'Left': 0.64,
                        'Top': 0.11,
                        'Width': 0.12},
                    'photo_id': '1'},
                'b5f0597b-e1da': {
                    'bounding_box': {
                        'Height': 0.32,
                        'Left': 0.34,
                        'Top': 0.20,
                        'Width': 0.13},
                    'photo_id': '1'}}
            return result

        def _mock_search_faces(collection_id, face_id):
            return ['48930575-3ea5']

        def _mock_get_bounding_box_info_from_dict(info_dict):
            return (0.1, 0.2, 0.3, 0.4)

        def _mock_make_cropped_face_image(photo_byte_string, photo_width, photo_height, face_width_percentage, face_height_percentage, face_top_percentage, face_left_percentage):
            return b'12345'

        def _mock_delete_rekognition_collection(collection_id):
            return None

        server.upload_file_to_s3 = _mock_upload_file_to_s3
        server.get_photo_bytestring_from_s3 = _mock_get_photo_bytestring_from_s3
        server.get_photo_width_height = _mock_get_photo_width_height
        server.create_rekognition_collection = _mock_create_rekognition_collection
        server.index_faces = _mock_index_faces
        server.get_face_id_external_image_id_dict = _mock_get_face_id_external_image_id_dict
        server.search_faces = _mock_search_faces
        server.get_bounding_box_info_from_dict = _mock_get_bounding_box_info_from_dict
        server.make_cropped_face_image = _mock_make_cropped_face_image
        server.delete_rekognition_collection = _mock_delete_rekognition_collection

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_upload(self):
        """Test can upload files."""
        data = {'name': 'test', 'photo': 12}
        data = {key: str(value) for key, value in data.items()}
        data['user_file'] = (io.BytesIO(b'abcdef'), 'test.jpg')
        response = self.client.post(
            '/upload', data=data, follow_redirects=True,
            content_type='multipart/form-data'
        )

        collection = Collection.query.get(1)
        self.assertIsNotNone(collection.time_processed)
        self.assertEqual(len(collection.photos), 1)
        self.assertEqual(len(collection.persons), 2)

        photo = collection.photos[0]
        self.assertEqual(photo.collection_id, 1)
        self.assertEqual(photo.s3_key, 'collection1/photo1.jpg')
        self.assertEqual(photo.byte_string, b'abcde')
        self.assertEqual(photo.width, 123)
        self.assertEqual(photo.height, 456)

        persons = collection.persons
        for person in persons:
            self.assertEqual(person.collection_id, 1)
            person_photo = PersonPhoto.query.filter(
                PersonPhoto.photo_id == photo.id,
                PersonPhoto.person_id == person.id
            ).all()
            for entry in person_photo:
                self.assertEqual(entry.face_width_percentage, 0.1)
                self.assertEqual(entry.face_height_percentage, 0.2)
                self.assertEqual(entry.face_top_percentage, 0.3)
                self.assertEqual(entry.face_left_percentage, 0.4)

        self.assertIn(b'Your collection of pictures was processed successfully!', response.data)


if __name__ == "__main__":
    unittest.main()
