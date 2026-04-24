"""
Trains API Routes
REST endpoints for train management
"""
from flask import Blueprint, jsonify

trains_bp = Blueprint('trains', __name__, url_prefix='/api/trains')


@trains_bp.route('', methods=['GET'])
def list_trains():
    """List all trains"""
    return jsonify({'success': True, 'data': [], 'message': 'Not implemented yet'}), 200


@trains_bp.route('/<int:train_id>', methods=['GET'])
def get_train(train_id):
    """Get a specific train"""
    return jsonify({'success': True, 'data': None}), 200
