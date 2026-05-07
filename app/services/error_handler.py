"""
Custom Exception Classes and Error Handler Registration
All API errors are returned as JSON with a consistent shape:

    {
        "success": false,
        "error_code": "NOT_FOUND",
        "message": "Human-readable description",
        "details": { ... }   (optional, only on validation errors)
    }
"""
from flask import jsonify


# ══════════════════════════════════════════════════════════════════════
# Custom Exception Classes
# ══════════════════════════════════════════════════════════════════════

class AppError(Exception):
    """
    Base class for all application errors.
    Subclasses set a default HTTP status and error_code.
    """
    http_status: int = 500
    error_code: str  = 'INTERNAL_ERROR'

    def __init__(self, message: str = 'An unexpected error occurred', details=None):
        super().__init__(message)
        self.message = message
        self.details = details  # optional dict / list for extra context

    def to_response(self):
        body = {
            'success': False,
            'error_code': self.error_code,
            'message': self.message,
        }
        if self.details is not None:
            body['details'] = self.details
        return jsonify(body), self.http_status


# ── 400 Bad Request ───────────────────────────────────────────

class ValidationError(AppError):
    """Raised when incoming request data fails validation."""
    http_status = 400
    error_code  = 'VALIDATION_ERROR'

    def __init__(self, message='Request data is invalid', errors=None):
        # `errors` may be a list of field-level messages
        super().__init__(message, details=errors)


class BadRequestError(AppError):
    """Generic bad-request error (malformed JSON, missing body, etc.)."""
    http_status = 400
    error_code  = 'BAD_REQUEST'


# ── 404 Not Found ─────────────────────────────────────────────

class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""
    http_status = 404
    error_code  = 'NOT_FOUND'

    def __init__(self, resource: str = 'Resource', resource_id=None):
        if resource_id is not None:
            msg = f'{resource} with id {resource_id} was not found'
        else:
            msg = f'{resource} not found'
        super().__init__(msg)


# ── 409 Conflict ──────────────────────────────────────────────

class ConflictError(AppError):
    """Raised when a create/update would violate a uniqueness constraint."""
    http_status = 409
    error_code  = 'CONFLICT'


# ── 422 Unprocessable ─────────────────────────────────────────

class BusinessRuleError(AppError):
    """
    Raised when an operation is syntactically valid but violates a
    business rule (e.g. booking a past schedule, double-booking a seat).
    """
    http_status = 422
    error_code  = 'BUSINESS_RULE_VIOLATION'


# ── 500 Server Error ──────────────────────────────────────────

class DatabaseError(AppError):
    """Raised when a database operation fails unexpectedly."""
    http_status = 500
    error_code  = 'DATABASE_ERROR'

    def __init__(self, message='A database error occurred', original_error=None):
        details = {'original_error': str(original_error)} if original_error else None
        super().__init__(message, details=details)


class ServiceError(AppError):
    """Generic service-layer error."""
    http_status = 500
    error_code  = 'SERVICE_ERROR'


# ══════════════════════════════════════════════════════════════════════
# Flask Error Handler Registration
# ══════════════════════════════════════════════════════════════════════

def register_error_handlers(app):
    """
    Register all error handlers on the Flask app.
    Call this from create_app() after registering blueprints.
    """

    # ── Custom AppError hierarchy ─────────────────────────────

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return error.to_response()

    # ── Standard HTTP errors ──────────────────────────────────

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error_code': 'BAD_REQUEST',
            'message': 'The request could not be understood by the server',
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error_code': 'NOT_FOUND',
            'message': 'The requested resource was not found',
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error_code': 'METHOD_NOT_ALLOWED',
            'message': 'HTTP method not allowed on this endpoint',
        }), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'success': False,
            'error_code': 'CONFLICT',
            'message': 'The request conflicts with the current state of the resource',
        }), 409

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error_code': 'UNPROCESSABLE_ENTITY',
            'message': 'The request was well-formed but could not be processed',
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': 'An unexpected internal server error occurred',
        }), 500

    # ── Catch-all for unhandled Python exceptions ─────────────

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception('Unhandled exception: %s', error)
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred. Please try again later.',
        }), 500


# ══════════════════════════════════════════════════════════════════════
# Convenience helpers (use in route handlers)
# ══════════════════════════════════════════════════════════════════════

def error_response(message: str, error_code: str = 'ERROR',
                   status: int = 400, details=None):
    """
    Return a Flask JSON error response without raising an exception.
    Use this for simple inline error returns in route handlers.

    Example:
        return error_response('Seat already booked', 'CONFLICT', 409)
    """
    body = {'success': False, 'error_code': error_code, 'message': message}
    if details is not None:
        body['details'] = details
    return jsonify(body), status


def success_response(data=None, message: str = None,
                     status: int = 200, **kwargs):
    """
    Return a standardised JSON success response.

    Example:
        return success_response(data=train, status=201)
        return success_response(data=list_result, count=len(list_result))
    """
    body = {'success': True}
    if message:
        body['message'] = message
    if data is not None:
        body['data'] = data
    body.update(kwargs)          # allow extra keys like count, meta, etc.
    return jsonify(body), status
