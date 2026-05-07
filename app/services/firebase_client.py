"""
Firebase Cloud Storage Service
Integration with Firebase for data backup and cloud storage
"""
import os
import json
from datetime import datetime
from firebase_admin import credentials, firestore, storage
import firebase_admin


class FirebaseClient:
    """Firebase Cloud client for backup and sync operations"""
    
    _db = None
    _storage = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return
        
        try:
            # Get credentials from environment or file
            creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
            
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Firebase credentials not found at {creds_path}")
            
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv('FIREBASE_BUCKET', 'railway-dbms.appspot.com')
            })
            
            cls._db = firestore.client()
            cls._storage = storage.bucket()
            cls._initialized = True
        except Exception as e:
            raise Exception(f"Firebase initialization failed: {str(e)}")
    
    @classmethod
    def backup_data(cls, collection_name, data):
        """
        Backup data to Firestore collection
        
        Args:
            collection_name: Firestore collection name
            data: Dictionary of documents to backup {doc_id: doc_data}
        
        Returns:
            Success status and count
        """
        if not cls._initialized:
            cls.initialize()
        
        try:
            batch_size = 100
            batch = cls._db.batch()
            count = 0
            
            for doc_id, doc_data in data.items():
                doc_ref = cls._db.collection(collection_name).document(str(doc_id))
                doc_data['backed_up_at'] = datetime.now().isoformat()
                batch.set(doc_ref, doc_data)
                count += 1
                
                if count % batch_size == 0:
                    batch.commit()
                    batch = cls._db.batch()
            
            if count % batch_size != 0:
                batch.commit()
            
            return {
                'success': True,
                'collection': collection_name,
                'documents_backed_up': count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def restore_data(cls, collection_name):
        """
        Restore data from Firestore collection
        
        Args:
            collection_name: Firestore collection name
        
        Returns:
            Dictionary of restored documents
        """
        if not cls._initialized:
            cls.initialize()
        
        try:
            docs = cls._db.collection(collection_name).stream()
            data = {}
            
            for doc in docs:
                data[doc.id] = doc.to_dict()
            
            return {
                'success': True,
                'collection': collection_name,
                'documents_restored': len(data),
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def upload_file(cls, file_path, destination_path):
        """
        Upload file to Firebase Storage
        
        Args:
            file_path: Local file path
            destination_path: Cloud storage path
        
        Returns:
            Success status and download URL
        """
        if not cls._initialized:
            cls.initialize()
        
        try:
            blob = cls._storage.blob(destination_path)
            blob.upload_from_filename(file_path)
            
            download_url = blob.public_url
            
            return {
                'success': True,
                'destination': destination_path,
                'download_url': download_url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def download_file(cls, source_path, destination_path):
        """
        Download file from Firebase Storage
        
        Args:
            source_path: Cloud storage path
            destination_path: Local destination path
        
        Returns:
            Success status
        """
        if not cls._initialized:
            cls.initialize()
        
        try:
            blob = cls._storage.blob(source_path)
            blob.download_to_filename(destination_path)
            
            return {
                'success': True,
                'source': source_path,
                'destination': destination_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def delete_file(cls, file_path):
        """Delete file from Firebase Storage"""
        if not cls._initialized:
            cls.initialize()
        
        try:
            blob = cls._storage.blob(file_path)
            blob.delete()
            
            return {
                'success': True,
                'deleted': file_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def get_backup_history(cls):
        """Get backup history from Firestore"""
        if not cls._initialized:
            cls.initialize()
        
        try:
            docs = cls._db.collection('backup_history').stream()
            history = []
            
            for doc in docs:
                history.append(doc.to_dict())
            
            return {
                'success': True,
                'backups': sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def save_backup_record(cls, backup_data):
        """Save backup metadata to Firestore"""
        if not cls._initialized:
            cls.initialize()
        
        try:
            doc_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_data['timestamp'] = datetime.now().isoformat()
            
            cls._db.collection('backup_history').document(doc_id).set(backup_data)
            
            return {
                'success': True,
                'backup_id': doc_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
