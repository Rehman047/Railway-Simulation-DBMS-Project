# Railway DBMS - Authentication & Authorization System

## Overview

The Railway DBMS project now includes a two-tier authentication system with **Admin** and **Simple User** roles.

### User Roles

#### 1. **Admin User**
- Full access to all operations
- **Required to enter password** to perform:
  - Add/Create trains, stations, routes, schedules
  - Update trains, stations, routes, schedules
  - Delete trains, stations, routes, schedules
- Session-based authentication (24-hour default timeout)
- Can logout to return to simple user mode

#### 2. **Simple User** (Default)
- Can view all data (read-only for most modules)
- Can perform booking operations:
  - Create new bookings
  - Cancel existing bookings
  - View booking history
- Can view passengers, trains, stations, routes, schedules
- No password required
- Full access to all read-only operations

## Configuration

### Setting the Admin Password

The admin password is configured via an environment variable. There are two ways to set it:

#### Method 1: Using `.env` file

Create or edit a `.env` file in the project root:

```env
ADMIN_PASSWORD=your_secure_password_here
```

#### Method 2: Environment Variable

Export the variable before running the app:

```bash
export ADMIN_PASSWORD="your_secure_password_here"
export FLASK_ENV=production
python run.py
```

#### Default Password

If no password is configured, the default is:
```
admin@railway123
```

⚠️ **WARNING**: Always change this password in production!

## Architecture

### Backend Components

#### 1. **app/config_secrets.py**
- Stores sensitive configuration including admin password
- Loads password from environment variables
- Configurable session timeout (default: 24 hours)

#### 2. **app/services/auth_service.py**
- Core authentication and authorization service
- Methods:
  - `verify_admin_password(password)` - Verifies password without setting session
  - `authenticate_admin(password)` - Sets admin session after password verification
  - `is_admin_authenticated()` - Checks if current session is authenticated as admin
  - `logout_admin()` - Clears admin session
  - `get_user_role()` - Returns current user role ('admin' or 'user')
- Decorators:
  - `@require_admin_auth` - Protects routes that require admin access

#### 3. **app/routes/auth.py**
- Authentication API endpoints:
  - `POST /api/auth/login` - Login with password
  - `POST /api/auth/logout` - Logout admin session
  - `GET /api/auth/status` - Get current authentication status
  - `POST /api/auth/verify-password` - Verify password without setting session

### Frontend Components

#### 1. **app/static/js/auth.js**
- Handles all authentication UI logic
- Functions:
  - `checkAuthStatus()` - Checks current authentication status
  - `openAuthModal()` - Opens login dialog
  - `closeAuthModal()` - Closes login dialog
  - `handleAdminLogin(event)` - Processes login form submission
  - `handleLogout()` - Logs out admin user
  - `makeAdminRequest(endpoint, options)` - Makes API calls with automatic auth handling
  - `retryPendingAdminRequest()` - Retries request after authentication

#### 2. **Authentication Modal** (in base.html)
- Displayed when user attempts admin operation without authentication
- Prompts for password
- Shows error messages for invalid password
- Shows success message after authentication

#### 3. **Authentication Button** (in topbar)
- Shows "Login (Admin)" when not authenticated
- Shows "Logout (Admin)" when authenticated
- Clicking calls `handleAuthClick()` or `handleLogout()`

### Protected Routes

The following API endpoints require admin authentication:

#### **Trains**
- `POST /api/trains` - Create train
- `PUT /api/trains/<id>` - Update train
- `DELETE /api/trains/<id>` - Delete train

#### **Stations**
- `POST /api/stations` - Create station
- `PUT /api/stations/<id>` - Update station
- `DELETE /api/stations/<id>` - Delete station

#### **Routes**
- `POST /api/routes` - Create route
- `PUT /api/routes/<id>` - Update route
- `DELETE /api/routes/<id>` - Delete route

#### **Schedules**
- `POST /api/schedules` - Create schedule
- `PUT /api/schedules/<id>` - Update schedule
- `DELETE /api/schedules/<id>` - Delete schedule

## Usage Flow

### For Simple Users (Default)

1. Open the application
2. View all data (trains, stations, passengers, etc.)
3. Can make bookings, cancel bookings, view history
4. No password required
5. Status shows "Simple User" in top-right

### For Admin Users

#### Logging In

1. Click "Login (Admin)" button in top-right
2. Enter admin password in the modal dialog
3. Click "Login as Admin"
4. On success, button changes to "Logout (Admin)" with green status
5. Now can perform admin operations

#### Performing Admin Operations

Once logged in as admin:

1. Navigate to Trains, Stations, Routes, or Schedules
2. Click "Add New Train" (or equivalent)
3. Fill in form and submit
4. Request is sent with admin authentication
5. Operation succeeds (no additional password prompt needed)

#### Session Expiration

- Admin session expires after 24 hours
- When trying admin operation after expiry, user is prompted to login again
- Simple users have no session timeout

#### Logging Out

1. Click "Logout (Admin)" button
2. Confirm logout
3. Button changes back to "Login (Admin)"
4. Page reloads

## API Responses

### Successful Admin Operation

```json
{
  "success": true,
  "train_id": 1,
  "message": "Train created successfully"
}
```

### Admin Authentication Required

```json
{
  "success": false,
  "error": "Admin authentication required",
  "requires_auth": true
}
Status: 403 Forbidden
```

### Invalid Password

```json
{
  "success": false,
  "error": "Invalid admin password"
}
Status: 401 Unauthorized
```

## Error Handling

### Frontend Error Handling

The auth.js file automatically handles:

1. **403 Forbidden** - Shows login modal, retries after authentication
2. **401 Unauthorized** - Shows error message in login modal
3. **Network errors** - Shows error alert with retry option
4. **Session timeout** - Prompts for re-authentication

### Backend Error Handling

The auth_service decorator returns:

- **403 Forbidden** - If session not authenticated as admin
- **401 Unauthorized** - If password is incorrect
- **400 Bad Request** - If required fields missing

## Making Admin Calls in Templates

### Using makeAdminRequest

For admin operations in template JavaScript:

```javascript
// Example: Create a train
await makeAdminRequest('/api/trains', {
    method: 'POST',
    body: JSON.stringify({
        train_name: 'Express Train 1',
        train_number: 'EXP-001',
        train_type: 'express',
        capacity: 500,
        total_coaches: 10
    })
});
```

The function automatically:
- Adds credentials
- Handles 403 errors by showing login modal
- Retries after successful authentication

### Legacy Fetch Pattern

If not using `makeAdminRequest`, check response status:

```javascript
const response = await fetch('/api/trains', {
    method: 'POST',
    credentials: 'include',  // Important!
    body: JSON.stringify(data)
});

if (response.status === 403) {
    openAuthModal();
    // Retry after authentication
} else if (response.ok) {
    // Success
} else {
    // Error
}
```

## Security Considerations

### Production Deployment

1. **Always set strong password** via environment variable
2. **Use HTTPS** - Never use HTTP for authentication
3. **Session configuration** - Adjust `SESSION_TIMEOUT` for your needs
4. **CSRF Protection** - Ensure Flask CSRF tokens are enabled
5. **Rate limiting** - Consider rate-limiting login attempts
6. **Logging** - Log all admin operations for audit trail

### Password Storage

- Passwords are NOT stored - only compared on login
- Session tokens are server-side and secure
- No personal data is transmitted in plaintext

### Session Security

- Sessions use secure cookies
- `SESSION_USE_SIGNER = True` - Prevents session tampering
- `SESSION_PERMANENT = False` - Session cleared on browser close (unless rememberme is used)
- Timeout: 24 hours (configurable via `SESSION_TIMEOUT`)

## Troubleshooting

### "Admin authentication required" message keeps appearing

**Solution**: 
1. Check if cookies are enabled in browser
2. Verify password is correct
3. Check browser console for errors (F12)
4. Try incognito/private window

### Password accepted but operations still fail

**Causes**:
1. Session expired - login again
2. Browser cookies disabled - enable them
3. HTTPS redirect issues - check browser redirect settings

**Solution**:
1. Click "Logout (Admin)" and login again
2. Check browser cookie settings
3. Clear browser cache and login again

### Default password not working

**Causes**:
1. Password was changed via environment variable
2. Configuration file missing or not loaded

**Solution**:
1. Check `.env` file or environment variables
2. Verify `ADMIN_PASSWORD` is set correctly
3. Restart the Flask application

### How to recover if password is lost

If you forgot the admin password:

1. Stop the Flask application
2. Set a new password:
   ```bash
   export ADMIN_PASSWORD="new_password_here"
   python run.py
   ```
3. Use the new password to login

## Future Enhancements

Potential improvements to the authentication system:

1. **Multiple admin users** - Database-backed user accounts
2. **Role-based access control (RBAC)** - More granular permissions
3. **Two-factor authentication (2FA)** - SMS or email verification
4. **Audit logging** - Track all admin operations with timestamps and user info
5. **API tokens** - For programmatic access
6. **OAuth2 integration** - For enterprise authentication
7. **Password reset functionality** - Email-based password reset
8. **IP whitelisting** - Restrict admin access to specific IPs

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review browser console logs (F12 → Console tab)
3. Check Flask server logs for errors
4. Verify environment variables are set correctly
