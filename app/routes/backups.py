"""
Backup & Restore API Routes
Endpoints for database backup and restoration
"""
from flask import Blueprint, jsonify, request
from app.services.backup_service import BackupService
from app.services.firebase_client import FirebaseClient
from app.utils.decorators import admin_required


backups_bp = Blueprint('backups', __name__, url_prefix='/api/backups')


@backups_bp.route('/create-firestore', methods=['POST'])
@admin_required
def create_firestore_backup():
    """Create full database backup to Firebase Firestore"""
    result = BackupService.backup_database_to_firestore()
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@backups_bp.route('/create-local', methods=['POST'])
@admin_required
def create_local_backup():
    """Create local JSON backup"""
    file_path = request.json.get('file_path') if request.is_json else None
    
    if not file_path:
        file_path = f'/tmp/railway_backup_{__import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    result = BackupService.backup_database_to_file(file_path)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@backups_bp.route('/restore-firestore/<collection_name>', methods=['POST'])
@admin_required
def restore_firestore_backup(collection_name):
    """Restore collection from Firebase Firestore"""
    result = BackupService.restore_from_firestore(collection_name)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@backups_bp.route('/restore-local', methods=['POST'])
@admin_required
def restore_local_backup():
    """Restore from local backup file"""
    file_path = request.json.get('file_path') if request.is_json else None
    
    if not file_path:
        return jsonify({
            'success': False,
            'error': 'file_path is required'
        }), 400
    
    result = BackupService.restore_from_file(file_path)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@backups_bp.route('/history', methods=['GET'])
@admin_required
def backup_history():
    """Get backup history"""
    result = BackupService.get_backup_history()
    return jsonify(result), 200


@backups_bp.route('/info', methods=['GET'])
@admin_required
def backup_info():
    """Get database and backup information"""
    result = BackupService.get_backup_info()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@backups_bp.route('/auto-backup', methods=['POST'])
@admin_required
def trigger_auto_backup():
    """Trigger automatic backup (both Firestore and local)"""
    try:
        firestore_result = BackupService.backup_database_to_firestore()
        
        local_file_path = f'/tmp/railway_auto_backup_{__import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        local_result = BackupService.backup_database_to_file(local_file_path)
        
        return jsonify({
            'success': firestore_result['success'] and local_result['success'],
            'firestore_backup': firestore_result,
            'local_backup': local_result
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
