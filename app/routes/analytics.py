"""Analytics API Routes"""
from flask import Blueprint, jsonify

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/revenue', methods=['GET'])
def revenue_report():
    return jsonify({'success': True, 'data': []}), 200
