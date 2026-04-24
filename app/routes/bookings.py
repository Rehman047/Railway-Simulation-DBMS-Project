"""Bookings API Routes"""
from flask import Blueprint, jsonify

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@bookings_bp.route('', methods=['GET'])
def list_bookings():
    return jsonify({'success': True, 'data': []}), 200
