"""Schedules API Routes"""
from flask import Blueprint, jsonify

schedules_bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

@schedules_bp.route('', methods=['GET'])
def list_schedules():
    return jsonify({'success': True, 'data': []}), 200
