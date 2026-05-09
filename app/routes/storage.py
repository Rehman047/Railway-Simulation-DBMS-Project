"""
File Storage API Routes
Endpoints for file and image uploads/downloads
"""
from flask import Blueprint, request, jsonify, send_file
from werkzeug.datastructures import FileStorage
from app.services.file_storage_service import FileStorageService
from app.services.firebase_client import FirebaseClient


storage_bp = Blueprint('storage', __name__, url_prefix='/api/storage')


@storage_bp.route('/upload/passenger/<int:passenger_id>', methods=['POST'])
def upload_passenger_image(passenger_id):
    """Upload passenger profile image"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file_obj = request.files['file']
    
    if file_obj.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    result = FileStorageService.save_passenger_image(passenger_id, file_obj)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@storage_bp.route('/upload/train/<int:train_id>', methods=['POST'])
def upload_train_image(train_id):
    """Upload train image"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file_obj = request.files['file']
    
    if file_obj.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    result = FileStorageService.save_train_image(train_id, file_obj)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@storage_bp.route('/upload/station/<int:station_id>', methods=['POST'])
def upload_station_image(station_id):
    """Upload station image"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file_obj = request.files['file']
    
    if file_obj.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    result = FileStorageService.save_station_image(station_id, file_obj)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@storage_bp.route('/file/<entity_type>/<int:entity_id>', methods=['GET'])
def get_file(entity_type, entity_id):
    """Get file download URL"""
    result = FileStorageService.get_file(entity_id, entity_type)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@storage_bp.route('/delete/<path:file_path>', methods=['DELETE'])
def delete_file(file_path):
    """Delete file from storage"""
    result = FileStorageService.delete_file(file_path)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@storage_bp.route('/usage', methods=['GET'])
def get_storage_usage():
    """Get storage usage statistics"""
    result = FileStorageService.get_storage_usage()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@storage_bp.route('/init', methods=['POST'])
def init_storage():
    """Initialize storage folders"""
    try:
        FileStorageService.init_upload_folder()
        return jsonify({
            'success': True,
            'message': 'Storage initialized successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
