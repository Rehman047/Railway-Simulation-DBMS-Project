from flask import Blueprint, jsonify, request

from app.db import Database
from app.queries.train_queries import (
    GET_TRAIN, LIST_TRAINS, COUNT_TRAINS, CREATE_TRAIN, UPDATE_TRAIN,
    GET_TRAIN_WITH_COACHES, GET_TRAIN_AMENITIES,
)
from app.queries.coach_queries import LIST_COACHES_BY_TRAIN
from app.services.firebase_client import FirebaseClient
from app.services.validators import validate_create_train

trains_bp = Blueprint('trains', __name__, url_prefix='/api/trains')


# ── List & Get ────────────────────────────────────────────────

@trains_bp.route('', methods=['GET'])
def list_trains():
    """List all trains with pagination. Optional filter: ?status=active&type=Express"""
    page  = request.args.get('page',   1,    type=int)
    limit = request.args.get('limit',  20,   type=int)
    status     = request.args.get('status',  type=str)
    train_type = request.args.get('type',    type=str)

    offset = (page - 1) * limit

    # Build dynamic WHERE
    conditions, params = [], []
    if status:
        conditions.append("LOWER(status) = LOWER(%s)")
        params.append(status)
    if train_type:
        conditions.append("LOWER(train_type) = LOWER(%s)")
        params.append(train_type)

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

    trains = Database.fetch_all(
        f"""SELECT train_id, train_name, train_number, train_type,
                   capacity, total_coaches, status, created_at
            FROM trains {where}
            ORDER BY train_name
            LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    total = Database.fetch_scalar(f"SELECT COUNT(*) FROM trains {where}", params)

    return jsonify({
        'success': True,
        'data': trains,
        'meta': {'page': page, 'limit': limit, 'total': total,
                 'pages': (total + limit - 1) // limit if total else 0},
    }), 200


@trains_bp.route('/<int:train_id>', methods=['GET'])
def get_train(train_id: int):
    """Get a specific train by ID."""
    train = Database.fetch_one(GET_TRAIN, (train_id,))
    if not train:
        return jsonify({'success': False, 'error': 'Train not found'}), 404
    return jsonify({'success': True, 'data': train}), 200


# ── Create ────────────────────────────────────────────────────

@trains_bp.route('', methods=['POST'])
def create_train():
    """
    Create a new train.
    Required JSON: train_name, train_number, train_type, capacity, total_coaches.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    errors = validate_create_train(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Check train_number uniqueness
    existing = Database.fetch_one(
        "SELECT train_id FROM trains WHERE train_number = %s", (data['train_number'],)
    )
    if existing:
        return jsonify({'success': False, 'error': 'Train number already exists'}), 400

    train_id = Database.execute_returning(
        CREATE_TRAIN,
        (data['train_name'], data['train_number'], data['train_type'],
         data['capacity'], data['total_coaches'], data.get('status', 'active'))
    )

    if train_id:
        try:
            FirebaseClient.backup_data('trains', {
                str(train_id): {
                    'train_name': data['train_name'],
                    'train_number': data['train_number'],
                    'train_type': data['train_type'],
                    'capacity': data['capacity'],
                    'total_coaches': data['total_coaches'],
                    'train_id': train_id,
                }
            })
        except Exception:
            pass
        return jsonify({'success': True, 'train_id': train_id}), 201
    return jsonify({'success': False, 'error': 'Failed to create train'}), 500


# ── Update ────────────────────────────────────────────────────

@trains_bp.route('/<int:train_id>', methods=['PUT'])
def update_train(train_id: int):
    """Update train info. Updatable fields: train_name, train_type, capacity, total_coaches, status."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    train = Database.fetch_one(GET_TRAIN, (train_id,))
    if not train:
        return jsonify({'success': False, 'error': 'Train not found'}), 404

    # Merge with existing values
    train_name    = data.get('train_name',    train['train_name'])
    train_type    = data.get('train_type',    train['train_type'])
    status        = data.get('status',        train['status'])

    try:
        capacity      = int(data.get('capacity',      train['capacity']))
        total_coaches = int(data.get('total_coaches', train['total_coaches']))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'capacity and total_coaches must be integers'}), 400

    affected = Database.execute(
        UPDATE_TRAIN, (train_name, train_type, capacity, total_coaches, status, train_id)
    )

    if affected > 0:
        try:
            FirebaseClient.backup_data('trains', {
                str(train_id): {
                    'train_name': train_name,
                    'train_type': train_type,
                    'capacity': capacity,
                    'total_coaches': total_coaches,
                    'status': status,
                    'train_id': train_id,
                }
            })
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Train updated successfully'}), 200
    return jsonify({'success': False, 'error': 'No changes made'}), 400


# ── Delete ────────────────────────────────────────────────────

@trains_bp.route('/<int:train_id>', methods=['DELETE'])
def delete_train(train_id: int):
    """Delete a train."""
    train = Database.fetch_one(GET_TRAIN, (train_id,))
    if not train:
        return jsonify({'success': False, 'error': 'Train not found'}), 404

    try:
        Database.execute("DELETE FROM trains WHERE train_id = %s", (train_id,))
        try:
            FirebaseClient.delete_document('trains', train_id)
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Train deleted successfully'}), 200
    except Exception as e:
        error_msg = str(e)
        # Check for foreign key constraint errors
        if 'foreign key constraint' in error_msg.lower():
            return jsonify({
                'success': False,
                'error': 'Cannot delete train: it has associated coaches or other dependent records'
            }), 409  # Conflict status
        return jsonify({'success': False, 'error': error_msg}), 400


# ── Sub-resources ─────────────────────────────────────────────

@trains_bp.route('/<int:train_id>/coaches', methods=['GET'])
def get_train_coaches(train_id: int):
    """Get all coaches for a train."""
    train = Database.fetch_one("SELECT train_id FROM trains WHERE train_id = %s", (train_id,))
    if not train:
        return jsonify({'success': False, 'error': 'Train not found'}), 404

    coaches = Database.fetch_all(LIST_COACHES_BY_TRAIN, (train_id,))
    return jsonify({'success': True, 'data': coaches, 'count': len(coaches)}), 200


@trains_bp.route('/<int:train_id>/amenities', methods=['GET'])
def get_train_amenities(train_id: int):
    """Get amenities available on a train."""
    train = Database.fetch_one("SELECT train_id FROM trains WHERE train_id = %s", (train_id,))
    if not train:
        return jsonify({'success': False, 'error': 'Train not found'}), 404

    amenities = Database.fetch_all(GET_TRAIN_AMENITIES, (train_id,))
    return jsonify({'success': True, 'data': amenities, 'count': len(amenities)}), 200
