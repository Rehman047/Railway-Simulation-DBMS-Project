"""Cancellations API Routes"""
from flask import Blueprint, jsonify

cancellations_bp = Blueprint('cancellations', __name__, url_prefix='/api/cancellations')

@cancellations_bp.route('', methods=['GET'])
def list_cancellations():
    return jsonify({'success': True, 'data': []}), 200
