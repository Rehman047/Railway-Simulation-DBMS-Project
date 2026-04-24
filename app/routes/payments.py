"""Payments API Routes"""
from flask import Blueprint, jsonify

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@payments_bp.route('', methods=['GET'])
def list_payments():
    return jsonify({'success': True, 'data': []}), 200
