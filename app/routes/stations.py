"""Stations API Routes"""
from flask import Blueprint, jsonify

stations_bp = Blueprint('stations', __name__, url_prefix='/api/stations')

@stations_bp.route('', methods=['GET'])
def list_stations():
    return jsonify({'success': True, 'data': []}), 200
