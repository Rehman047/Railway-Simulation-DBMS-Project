# Railway Simulation DBMS

A comprehensive Flask-based Railway Management System with PostgreSQL backend, featuring advanced booking management, analytics, backup, and cloud integration.

## Features

- **Complete Railway Management**: Trains, stations, routes, and schedules
- **Booking System**: Passenger bookings with seat allocation and fare calculation
- **Payment Processing**: Multiple payment methods with transaction tracking
- **Cancellation Management**: Refund policies and cancellation history
- **Analytics Dashboard**: Revenue tracking, occupancy analysis, and performance metrics
- **Database Procedures**: Advanced SQL procedures for complex operations
- **Firebase Integration**: Cloud backup and data synchronization
- **File Storage**: Image upload and cloud storage support
- **Two-Tier Authentication System**: Admin and Simple User roles with password-protected admin operations
- **RESTful API**: Complete JSON API with pagination and filtering

## Tech Stack

- **Backend**: Flask 3.1.3 (Python web framework)
- **Database**: PostgreSQL (with advanced features: procedures, functions, views, triggers)
- **Frontend**: HTML5, CSS3 (glassmorphism design), Vanilla JavaScript ES6+
- **Cloud**: Firebase (Firestore, Cloud Storage)
- **Connection Pool**: psycopg2 with SimpleConnectionPool

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+

### Installation

```bash
# Clone repository
git clone https://github.com/yourrepo/railway-simulation-dbms.git
cd Railway-Simulation-DBMS-Project

# Create virtual environment
python3 -m venv zenv
source zenv/bin/activate  # Windows: zenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup .env file (see Configuration section)
cp .env.example .env

# Initialize database
psql -U postgres -d railway_db -f database/schema.sql
psql -U postgres -d railway_db -f database/seed.sql
psql -U postgres -d railway_db -f database/indexes.sql
psql -U postgres -d railway_db -f database/views_procedures.sql

# Start application
python run.py
```

Visit `http://localhost:5000` to access the dashboard.

## Authentication System

The application uses a **two-tier user system**:

### Admin User
- Can add/delete/edit trains, stations, routes, and schedules
- Requires password authentication for admin operations
- Session-based (24-hour default timeout)

### Simple User (Default)
- Can view all data
- Can make and cancel bookings
- No password required

### Setting Admin Password

```env
# In .env file or environment variable
ADMIN_PASSWORD=your_secure_password_here
```

Default password (change in production): `admin@railway123`

**For detailed documentation, see [AUTHENTICATION.md](AUTHENTICATION.md)**

## Project Structure

```
app/
├── routes/              # Flask API blueprints
├── services/            # Business logic layer
├── queries/             # SQL query definitions
├── templates/           # HTML Jinja2 templates
├── static/              # CSS and JavaScript
└── utils/               # Validators, decorators, mappers

database/
├── schema.sql           # Database tables
├── seed.sql             # Sample data
├── indexes.sql          # Performance indexes
└── views_procedures.sql # Advanced SQL features
```

## Configuration

Create `.env` file with:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=railway_db
DB_USER=postgres
DB_PASSWORD=your_password
FLASK_ENV=development
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

## API Endpoints

### Passengers
- `GET /api/passengers` - List passengers
- `POST /api/passengers` - Create passenger
- `GET /api/passengers/{id}` - Get passenger
- `PUT /api/passengers/{id}` - Update passenger
- `DELETE /api/passengers/{id}` - Delete passenger

### Bookings
- `GET /api/bookings` - List bookings
- `POST /api/bookings` - Create booking
- `GET /api/bookings/{id}` - Get booking
- `POST /api/bookings/{id}/cancel` - Cancel booking
- `GET /api/bookings/available-seats/{schedule_id}` - Available seats

### Trains
- `GET /api/trains` - List trains
- `POST /api/trains` - Create train
- `GET /api/trains/{id}` - Get train

### Schedules
- `GET /api/schedules` - List schedules
- `POST /api/schedules` - Create schedule
- `GET /api/schedules/{id}` - Get schedule

### Analytics
- `GET /api/analytics/dashboard` - Dashboard summary
- `GET /api/analytics/revenue/by-train` - Revenue by train
- `GET /api/analytics/occupancy` - Occupancy metrics
- `GET /api/analytics/top-routes` - Top routes

### Backup & Storage
- `POST /api/backups/auto-backup` - Automatic backup
- `POST /api/storage/upload/passenger/{id}` - Upload image
- `GET /api/storage/usage` - Storage usage

## Database Schema

### Core Tables
- `passengers` - Passenger information
- `trains` - Train details
- `stations` - Station locations
- `routes` - Train routes
- `schedules` - Train schedules
- `bookings` - Booking records
- `payments` - Payment transactions
- `cancellations` - Cancellation records
- `staff` - Staff members

### Advanced Features
- **Procedures**: Atomic operations (bookings, refunds)
- **Views**: Analytics, reporting, audit trails
- **Triggers**: Automatic seat availability, status updates
- **Functions**: Fare calculation, occupancy analysis

## Usage

### Web Interface
1. Navigate to http://localhost:5000/dashboard
2. Login with admin credentials
3. Manage bookings, passengers, trains, schedules

### API Example
```bash
curl -X POST http://localhost:5000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "passenger_id": 1,
    "schedule_id": 5,
    "seat_id": 12,
    "fare_amount": 500.00
  }'
```

## Deployment

### Development
```bash
python run.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker
```bash
docker build -t railway-dbms .
docker run -p 5000:5000 railway-dbms
```

## Security

- Credentials stored in `.env` file
- Input validation on all endpoints
- Parameterized SQL queries
- Role-based access control
- Session-based authentication

## Troubleshooting

### Database Connection
```bash
psql -h localhost -U postgres -d railway_db
```

### Clear Cache
```bash
rm -rf __pycache__ .pytest_cache
```

### Reset Database
```bash
dropdb railway_db
createdb railway_db
psql -U postgres -d railway_db -f database/schema.sql
```

## License

MIT

## Contact

For support, email support@railway-system.com