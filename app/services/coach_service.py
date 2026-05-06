"""
Coach Service Layer
Business logic for coach operations.
Uses direct database queries via app.db module.
"""
from app.db import Database
from app.queries.coach_queries import (
    GET_COACH,
    LIST_COACHES_BY_TRAIN,
    CREATE_COACH,
    UPDATE_COACH,
    DELETE_COACH,
    GET_COACH_WITH_SEATS,
    COUNT_BOOKED_SEATS_IN_COACH,
    GET_COACH_OCCUPANCY,
)


class CoachService:
    """Service for managing coach operations."""

    # ── Read ─────────────────────────────────────────────────────

    @staticmethod
    def get_coach(coach_id):
        """Get a single coach by ID."""
        return Database.fetch_one(GET_COACH, (coach_id,))

    @staticmethod
    def list_coaches_by_train(train_id):
        """Fetch all coaches belonging to a specific train."""
        return Database.fetch_all(LIST_COACHES_BY_TRAIN, (train_id,))

    # ── Create ───────────────────────────────────────────────────

    @staticmethod
    def create_coach(data):
        """
        Create a new coach.

        Required fields: train_id, coach_number, coach_type, total_seats.
        coach_status defaults to 'available' if not supplied.

        Returns:
            {'success': True, 'coach_id': <id>}  on success
            {'success': False, 'error': <msg>}    on failure
        """
        required_fields = ['train_id', 'coach_number', 'coach_type', 'total_seats']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return {'success': False, 'error': f'Missing required field: {field}'}

        try:
            total_seats = int(data['total_seats'])
            if total_seats <= 0:
                return {'success': False, 'error': 'total_seats must be greater than 0'}
        except (ValueError, TypeError):
            return {'success': False, 'error': 'total_seats must be a valid integer'}

        coach_status = data.get('coach_status', 'available')

        try:
            coach_id = Database.execute_returning(
                CREATE_COACH,
                (
                    data['train_id'],
                    data['coach_number'],
                    data['coach_type'],
                    total_seats,
                    coach_status,
                )
            )

            if coach_id:
                return {'success': True, 'coach_id': coach_id}
            return {'success': False, 'error': 'Failed to create coach'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ── Update ───────────────────────────────────────────────────

    @staticmethod
    def update_coach(coach_id, data):
        """
        Update coach_type, total_seats, and/or coach_status.

        Fetches the existing record so callers only need to supply the
        fields they want to change; unchanged fields keep their current values.

        Returns:
            {'success': True, 'message': ...}  on success
            {'success': False, 'error': ...}   on failure
        """
        coach = CoachService.get_coach(coach_id)
        if not coach:
            return {'success': False, 'error': 'Coach not found'}

        coach_type   = data.get('coach_type',   coach['coach_type'])
        coach_status = data.get('coach_status', coach['coach_status'])

        # Validate total_seats if provided
        if 'total_seats' in data:
            try:
                total_seats = int(data['total_seats'])
                if total_seats <= 0:
                    return {'success': False, 'error': 'total_seats must be greater than 0'}
            except (ValueError, TypeError):
                return {'success': False, 'error': 'total_seats must be a valid integer'}
        else:
            total_seats = coach['total_seats']

        try:
            affected = Database.execute(
                UPDATE_COACH,
                (coach_type, total_seats, coach_status, coach_id)
            )

            if affected > 0:
                return {'success': True, 'message': 'Coach updated successfully'}
            return {'success': False, 'error': 'Coach not found or no changes made'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ── Delete ───────────────────────────────────────────────────

    @staticmethod
    def delete_coach(coach_id):
        """
        Delete a coach only if none of its seats are currently booked.

        Returns:
            {'success': True, 'message': ...}  on success
            {'success': False, 'error': ...}   on failure
        """
        coach = CoachService.get_coach(coach_id)
        if not coach:
            return {'success': False, 'error': 'Coach not found'}

        booked_seats = Database.fetch_scalar(
            COUNT_BOOKED_SEATS_IN_COACH, (coach_id,)
        )

        if booked_seats and booked_seats > 0:
            return {
                'success': False,
                'error': f'Cannot delete coach: {booked_seats} seat(s) are currently booked'
            }

        try:
            affected = Database.execute(DELETE_COACH, (coach_id,))

            if affected > 0:
                return {'success': True, 'message': 'Coach deleted successfully'}
            return {'success': False, 'error': 'Failed to delete coach'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ── Detail views ─────────────────────────────────────────────

    @staticmethod
    def get_coach_with_seats(coach_id):
        """
        Fetch coach details together with all of its seats.

        Returns a list of rows (one per seat); the coach fields repeat on
        every row — callers should group by coach_id if needed.
        Returns an empty list if the coach does not exist.
        """
        return Database.fetch_all(GET_COACH_WITH_SEATS, (coach_id,))

    @staticmethod
    def get_coach_occupancy(coach_id):
        """
        Fetch occupancy statistics for a coach.

        Returns a dict with:
            coach_id, coach_number, total_seats,
            booked_seats, occupancy_percentage
        Or None if the coach does not exist.
        """
        return Database.fetch_one(GET_COACH_OCCUPANCY, (coach_id,))
