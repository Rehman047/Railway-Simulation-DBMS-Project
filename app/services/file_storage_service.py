"""
File & Image Storage Service
Handles local and cloud storage of images and documents
"""
import os
import hashlib
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from app.db import Database
from app.services.firebase_client import FirebaseClient


class FileStorageService:
    """Service for file and image storage management"""
    
    # Configuration
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'doc', 'docx'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    
    @staticmethod
    def init_upload_folder():
        """Initialize upload folder structure"""
        folders = [
            os.path.join(FileStorageService.UPLOAD_FOLDER, 'passengers'),
            os.path.join(FileStorageService.UPLOAD_FOLDER, 'trains'),
            os.path.join(FileStorageService.UPLOAD_FOLDER, 'stations'),
            os.path.join(FileStorageService.UPLOAD_FOLDER, 'documents')
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in FileStorageService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_hash(file_obj):
        """Generate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: file_obj.read(4096), b""):
            hash_md5.update(chunk)
        file_obj.seek(0)
        return hash_md5.hexdigest()
    
    @staticmethod
    def save_passenger_image(passenger_id, file_obj):
        """
        Save passenger profile image
        
        Args:
            passenger_id: Passenger ID
            file_obj: File object from Flask request
        
        Returns:
            Save status and file path
        """
        try:
            # Check file size by reading content
            content = file_obj.read()
            file_obj.seek(0)  # Reset pointer for later save
            if len(content) > FileStorageService.MAX_FILE_SIZE:
                return {
                    'success': False,
                    'error': 'File size exceeds 5MB limit'
                }
            
            if not FileStorageService.allowed_file(file_obj.filename):
                return {
                    'success': False,
                    'error': 'File type not allowed'
                }
            
            # Generate secure filename
            ext = file_obj.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f'passenger_{passenger_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}')
            
            # Save locally
            local_path = os.path.join(FileStorageService.UPLOAD_FOLDER, 'passengers', filename)
            file_obj.save(local_path)
            
            # Save to Firebase
            firebase_path = f'passengers/{passenger_id}/{filename}'
            firebase_result = FirebaseClient.upload_file(local_path, firebase_path)
            
            # Update database
            if firebase_result['success']:
                Database.execute(
                    "UPDATE passengers SET profile_image = %s WHERE passenger_id = %s",
                    (firebase_result['download_url'], passenger_id)
                )
            
            return {
                'success': True,
                'local_path': local_path,
                'cloud_path': firebase_path,
                'download_url': firebase_result.get('download_url'),
                'filename': filename
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def save_train_image(train_id, file_obj):
        """Save train image"""
        try:
            # Check file size by reading content
            content = file_obj.read()
            file_obj.seek(0)  # Reset pointer for later save
            if len(content) > FileStorageService.MAX_FILE_SIZE:
                return {
                    'success': False,
                    'error': 'File size exceeds 5MB limit'
                }
            
            if not FileStorageService.allowed_file(file_obj.filename):
                return {
                    'success': False,
                    'error': 'File type not allowed'
                }
            
            ext = file_obj.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f'train_{train_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}')
            
            local_path = os.path.join(FileStorageService.UPLOAD_FOLDER, 'trains', filename)
            file_obj.save(local_path)
            
            firebase_path = f'trains/{train_id}/{filename}'
            firebase_result = FirebaseClient.upload_file(local_path, firebase_path)
            
            if firebase_result['success']:
                Database.execute(
                    "UPDATE trains SET train_photo = %s WHERE train_id = %s",
                    (firebase_result['download_url'], train_id)
                )
            
            return {
                'success': True,
                'local_path': local_path,
                'cloud_path': firebase_path,
                'download_url': firebase_result.get('download_url'),
                'filename': filename
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def save_station_image(station_id, file_obj):
        """Save station image"""
        try:
            # Check file size by reading content
            content = file_obj.read()
            file_obj.seek(0)  # Reset pointer for later save
            if len(content) > FileStorageService.MAX_FILE_SIZE:
                return {
                    'success': False,
                    'error': 'File size exceeds 5MB limit'
                }
            
            if not FileStorageService.allowed_file(file_obj.filename):
                return {
                    'success': False,
                    'error': 'File type not allowed'
                }
            
            ext = file_obj.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f'station_{station_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}')
            
            local_path = os.path.join(FileStorageService.UPLOAD_FOLDER, 'stations', filename)
            file_obj.save(local_path)
            
            firebase_path = f'stations/{station_id}/{filename}'
            firebase_result = FirebaseClient.upload_file(local_path, firebase_path)
            
            if firebase_result['success']:
                Database.execute(
                    "UPDATE stations SET station_photo = %s WHERE station_id = %s",
                    (firebase_result['download_url'], station_id)
                )
            
            return {
                'success': True,
                'local_path': local_path,
                'cloud_path': firebase_path,
                'download_url': firebase_result.get('download_url'),
                'filename': filename
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_file(file_id, entity_type):
        """
        Get file download URL
        
        Args:
            file_id: ID of entity
            entity_type: Type (passenger, train, station)
        
        Returns:
            File metadata and URL
        """
        try:
            if entity_type == 'passenger':
                table = 'passengers'
                column = 'profile_image'
            elif entity_type == 'train':
                table = 'trains'
                column = 'train_photo'
            elif entity_type == 'station':
                table = 'stations'
                column = 'station_photo'
            else:
                return {'success': False, 'error': 'Invalid entity type'}
            
            query = f"SELECT {column} FROM {table} WHERE {entity_type}_id = %s"
            result = Database.fetch_one(query, (file_id,))
            
            if result and result[column]:
                return {
                    'success': True,
                    'download_url': result[column],
                    'entity_id': file_id,
                    'entity_type': entity_type
                }
            else:
                return {
                    'success': False,
                    'error': 'File not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_file(file_path):
        """Delete file from storage"""
        try:
            result = FirebaseClient.delete_file(file_path)
            
            # Also try to delete local copy
            local_file = os.path.join(FileStorageService.UPLOAD_FOLDER, file_path.split('/')[-1])
            if os.path.exists(local_file):
                os.remove(local_file)
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_storage_usage():
        """Get storage usage statistics"""
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(FileStorageService.UPLOAD_FOLDER):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                'success': True,
                'total_files': file_count,
                'total_size_mb': total_size / (1024 * 1024),
                'upload_folder': FileStorageService.UPLOAD_FOLDER
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
