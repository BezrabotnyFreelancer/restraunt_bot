import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firestore_client_config import CONFIG


class FirestoreClient:
    def __init__(self):
        self.config = CONFIG
        self.db_client = self.get_client(self.config)

    @staticmethod
    def get_client(config):
        cred = credentials.Certificate(config)
        firebase_admin.initialize_app(cred, {'projectId': CONFIG['project_id']})
        return firestore.client()

    def get_document(self, collection_id, document_id):
        return self.db_client.collection(collection_id).document(document_id).get().to_dict()

    def set_document(self, collection_id, document_id, data):
        self.db_client.collection(collection_id).document(document_id).set(data)

    def update_document(self, collection_id, document_id, data):
        self.db_client.collection(collection_id).document(document_id).update(data)

    def add_info_in_array(self, collection_id, document_id, field, data):
        self.update_document(collection_id, document_id, {field: firestore.ArrayUnion([data])})

    def delete_field(self, collection_id, document_id, field):
        self.update_document(collection_id, document_id, {field: firestore.DELETE_FIELD})


if __name__ == '__main__':
    firestore_client = FirestoreClient()
    firestore_client.set_document('test_collection', 'document1', {'1': 2, '3': 3})
    document = firestore_client.get_document('test_collection', 'document1')
    print(document)
