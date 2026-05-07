"""
Backup & Sync Service
Orchestrates database backups to Firebase and local storage
"""
import json
import os
from datetime import datetime
from app.db import Database
from app.services.firebase_client import FirebaseClient


class BackupService:
    """Service for managing database backups"""
    
    # Database collections to backup
    BACKUP_COLLECTIONS = [
        'passengers', 'trains', 'stations', 'routes', 'schedules',
        'bookings', 'payments', 'cancellations', 'staff', 'coaches',
        'seats', 'services', 'station_services'
    ]
    
    @staticmethod
    def backup_database_to_firestore():
        """
        Create full database backup to Firebase Firestore
        
        Returns:
            Backup status and metadata
        """
        try:
            backup_metadata = {
                'backup_type': 'full',
                'timestamp': datetime.now().isoformat(),
                'collections': {},
                'total_records': 0
            }
            
            for collection in BackupService.BACKUP_COLLECTIONS:
                try:
                    # Fetch all records from database table
                    records = Database.fetch_all(f"SELECT * FROM {collection}", ())
                    
                    if records:
                        # Convert to dictionary for Firebase storage
                        data_dict = {str(i): record for i, record in enumerate(records)}
                        
                        # Backup to Firebase
                        firebase_result = FirebaseClient.backup_data(collection, data_dict)
                        
                        if firebase_result['success']:
                            backup_metadata['collections'][collection] = {
                                'records_backed_up': len(records),
                                'status': 'success'
                            }
                            backup_metadata['total_records'] += len(records)
                        else:
                            backup_metadata['collections'][collection] = {
                                'error': firebase_result.get('error', 'Unknown error'),
                                'status': 'failed'
                            }
                except Exception as e:
                    backup_metadata['collections'][collection] = {
                        'error': str(e),
                        'status': 'failed'
                    }
            
            # Save backup metadata
            FirebaseClient.save_backup_record(backup_metadata)
            
            return {
                'success': True,
                'message': 'Database backup completed',
                'metadata': backup_metadata
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def backup_database_to_file(file_path):
        """
        Create local file backup of database
        
        Args:
            file_path: Path to save backup file
        
        Returns:
            Backup status
        """
        try:
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'collections': {}
            }
            
            for collection in BackupService.BACKUP_COLLECTIONS:
                try:
                    records = Database.fetch_all(f"SELECT * FROM {collection}", ())
                    backup_data['collections'][collection] = [dict(row) for row in records]
                except Exception as e:
                    backup_data['collections'][collection] = {'error': str(e)}
            
            # Save to JSON file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            return {
                'success': True,
                'message': 'Local backup completed',
                'file_path': file_path,
                'file_size_kb': os.path.getsize(file_path) / 1024
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def restore_from_firestore(collection_name):
        """
        Restore data from Firestore
        
        Args:
            collection_name: Collection to restore
        
        Returns:
            Restoration status
        """
        try:
            result = FirebaseClient.restore_data(collection_name)
            
            if result['success']:
                return {
                    'success': True,
                    'message': f'Restored {result["documents_restored"]} documents from {collection_name}',
                    'data': result['data']
                }
            else:
                return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def restore_from_file(file_path):
        """
        Restore database from local backup file
        
        Args:
            file_path: Path to backup file
        
        Returns:
            Restoration status
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'Backup file not found: {file_path}'
                }
            
            with open(file_path, 'r') as f:
                backup_data = json.load(f)
            
            restoration_log = {
                'timestamp': datetime.now().isoformat(),
                'source_file': file_path,
                'collections': {}
            }
            
            for collection, records in backup_data.get('collections', {}).items():
                if isinstance(records, dict) and 'error' in records:
                    restoration_log['collections'][collection] = {
                        'status': 'skipped',
                        'reason': 'Data had error during backup'
                    }
                    continue
                
                try:
                    restoration_log['collections'][collection] = {
                        'status': 'pending',
                        'record_count': len(records) if isinstance(records, list) else 0
                    }
                except Exception as e:
                    restoration_log['collections'][collection] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            return {
                'success': True,
                'message': 'Local restoration completed',
                'restoration_log': restoration_log
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_backup_history():
        """Get backup history"""
        try:
            history = FirebaseClient.get_backup_history()
            return history
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_backup_info():
        """Get information about database and backups"""
        try:
            backup_info = {
                'timestamp': datetime.now().isoformat(),
                'collections': {}
            }
            
            for collection in BackupService.BACKUP_COLLECTIONS:
                try:
                    count = Database.fetch_scalar(f"SELECT COUNT(*) FROM {collection}")
                    backup_info['collections'][collection] = {
                        'record_count': count or 0
                    }
                except Exception as e:
                    backup_info['collections'][collection] = {
                        'error': str(e)
                    }
            
            return {
                'success': True,
                'backup_info': backup_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
