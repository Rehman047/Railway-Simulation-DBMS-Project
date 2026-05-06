# Railway Simulation DBMS Project

## Overview

The Railway Simulation Database Management System is a comprehensive full-stack application for managing railway operations including trains, stations, passengers, schedules, bookings, payments, and cancellations. The system demonstrates advanced database concepts with PostgreSQL stored procedures, functions, views, triggers, and transactions.

## Problem Statement

Railway management requires efficient handling of:
- Multiple trains with varying capacities and routes
- Station networks across regions
- Passenger registration and booking
- Seat availability and occupancy tracking
- Payment processing and verification
- Cancellation policies with refund calculations
- Real-time analytics and reporting

## Key Features

### 1. **Train Management**
- Add, update, and delete trains
- Track coaches and amenities per train
- Monitor train status (active, maintenance, inactive)
- View train occupancy in real-time

### 2. **Station Management**
- Maintain network of stations
- Associate services available at each station
- Track station locations and contact information

### 3. **Schedule Management**
- Create schedules for train routes
- Manage departure and arrival times
- Track schedule status (scheduled, running, completed, cancelled)
- View available seats per schedule

### 4. **Passenger Management**
- Register new passengers with ID proof
- Maintain passenger information
- Track booking history
- Search and filter passengers

### 5. **Booking System**
- Create bookings with seat selection
- ACID transaction support for data consistency
- Prevent double booking through triggers
- Track booking status

### 6. **Payment Processing**
- Process payments for bookings
- Verify payment completion
- Audit trail for all payment changes
- Support multiple payment methods

### 7. **Cancellation & Refunds**
- Process booking cancellations
- Automatic refund calculation based on policy
- Refund tracking and status
- Audit logging

### 8. **Analytics & Reporting**
- Revenue reports by route
- Occupancy statistics
- Passenger growth tracking
- Top routes analysis
- Cancellation rate monitoring

## Technology Stack

### Backend
- **Framework**: Flask 3.1.3
- **Language**: Python
- **Database**: PostgreSQL with advanced features
- **ORM**: Direct psycopg2 queries

### Frontend
- **Markup**: HTML5
- **Styling**: CSS3 with glassmorphism design
- **Scripting**: Vanilla JavaScript (ES6+)
- **UI Components**: Custom modals, tables, forms

### Database Features
- **Stored Procedures**: 5+ for critical operations
- **Functions**: 6+ for calculations and validations
- **Views**: 6+ for analytics and reporting
- **Triggers**: 6+ for data integrity and automation
- **Indexes**: Strategic indexes for performance
- **Transactions**: ACID compliance for bookings and payments
- **Audit Logging**: Payment and cancellation tracking

## Project Structure

```
Railway-Simulation-DBMS-Project/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── db.py                     # Database connection pooling
│   ├── queries/                  # SQL query definitions
│   │   ├── passenger_queries.py
│   │   ├── train_queries.py
│   │   ├── booking_queries.py
│   │   ├── payment_queries.py
│   │   ├── cancellation_queries.py
│   │   └── ...
│   ├── services/                 # Business logic layer
│   │   ├── passenger_service.py
│   │   ├── booking_service.py
│   │   ├── payment_service.py
│   │   └── ...
│   ├── routes/                   # API endpoints
│   │   ├── passengers.py
│   │   ├── trains.py
│   │   ├── bookings.py
│   │   ├── payments.py
│   │   ├── analytics.py
│   │   └── ...
│   ├── static/                   # Static files
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   ├── forms.css
│   │   │   └── tables.css
│   │   └── js/
│   │       ├── utils.js
│   │       └── charts.js (optional)
│   ├── templates/                # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── passengers.html
│   │   ├── trains.html
│   │   ├── bookings.html
│   │   ├── analytics.html
│   │   └── ...
│   └── utils/                    # Utility modules
│       ├── validators.py
│       ├── error_handlers.py
│       └── result_mappers.py
├── database/
│   ├── schema.sql               # Main database schema
│   ├── views_procedures.sql     # Functions, procedures, views, triggers
│   ├── indexes.sql              # Performance indexes
│   ├── transactions.sql         # Transaction patterns
│   └── seed.sql                 # Sample data
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Database Schema

### Main Tables
1. **passengers** - Registered users
2. **trains** - Train information
3. **coaches** - Train coaches
4. **seats** - Individual seats
5. **stations** - Railway stations
6. **routes** - Train routes
7. **schedules** - Train schedules
8. **bookings** - Passenger bookings
9. **payments** - Payment records
10. **cancellations** - Cancellation records
11. **staff** - System staff
12. **amenities** - Train amenities
13. **services** - Station services

### Key Relationships
- `trains` → `coaches` → `seats`
- `stations` ← `routes` → `trains`
- `bookings` → `schedules` → `routes`
- `bookings` → `payments`
- `bookings` → `cancellations`

## API Endpoints

### Passengers
- `GET /api/passengers` - List all passengers
- `GET /api/passengers/<id>` - Get passenger details
- `POST /api/passengers` - Create new passenger
- `PUT /api/passengers/<id>` - Update passenger
- `DELETE /api/passengers/<id>` - Delete passenger
- `GET /api/passengers/<id>/bookings` - Get passenger bookings

### Trains
- `GET /api/trains` - List all trains
- `GET /api/trains/<id>` - Get train details
- `POST /api/trains` - Create new train
- `PUT /api/trains/<id>` - Update train
- `DELETE /api/trains/<id>` - Delete train
- `GET /api/trains/<id>/coaches` - Get train coaches
- `GET /api/trains/<id>/amenities` - Get train amenities

### Bookings
- `GET /api/bookings` - List bookings
- `GET /api/bookings/<id>` - Get booking details
- `POST /api/bookings` - Create booking
- `PUT /api/bookings/<id>` - Update booking
- `GET /api/bookings/passenger/<id>` - Get passenger bookings
- `GET /api/bookings/<id>/available-seats` - Get available seats

### Payments
- `GET /api/payments` - List payments
- `GET /api/payments/<id>` - Get payment details
- `POST /api/payments` - Create payment
- `PUT /api/payments/<id>/verify` - Verify payment
- `GET /api/payments/pending` - Get pending payments

### Cancellations
- `GET /api/cancellations` - List cancellations
- `GET /api/cancellations/<id>` - Get cancellation details
- `POST /api/cancellations` - Create cancellation
- `PUT /api/cancellations/<id>/process-refund` - Process refund
- `GET /api/cancellations/pending-refunds` - Get pending refunds

### Analytics
- `GET /api/analytics/revenue` - Total revenue
- `GET /api/analytics/revenue-by-route` - Revenue per route
- `GET /api/analytics/occupancy` - Occupancy statistics
- `GET /api/analytics/top-routes` - Top performing routes
- `GET /api/analytics/passenger-stats` - Passenger statistics

## Database Functions

### calculate_fare(route_id, seat_class)
Calculates fare based on distance and seat class
- Economy: 1.0x multiplier
- Business: 1.5x multiplier
- First Class: 2.0x multiplier

### get_available_seats(schedule_id)
Returns count of available seats for a schedule

### calculate_refund_amount(booking_id)
Calculates refund based on cancellation policy
- 7+ days before: 100% refund
- 3-7 days before: 75% refund
- 1-3 days before: 50% refund
- Within 24 hours: No refund

### validate_passenger_info(email, phone, age)
Validates passenger information format

### get_passenger_booking_history(passenger_id)
Returns all bookings for a passenger with details

## Database Stored Procedures

### add_booking(passenger_id, schedule_id, seat_id, fare_amount)
Creates a booking with transaction safety and prevents double booking

### process_cancellation(booking_id, staff_id, reason)
Processes cancellation, calculates refund, and updates records

### generate_revenue_report(start_date, end_date)
Generates revenue report for date range by route

### update_seat_availability(schedule_id, status)
Updates seat availability status for a schedule

### check_train_availability(schedule_id)
Returns seat availability statistics for a train

## Database Views

### passenger_complete_booking_info
Joins passenger, booking, payment, schedule, and station data

### revenue_by_route
Revenue analysis grouped by route

### train_occupancy_status
Real-time occupancy percentage for all trains

### pending_refunds_report
Lists all pending refunds with passenger information

### available_trains_by_route
Shows available trains between two stations

### staff_cancellation_stats
Statistics on cancellations processed by each staff member

## Database Triggers

### trg_after_booking_insert
Automatically updates seat status to 'booked' when booking created

### trg_after_payment_complete
Confirms booking when payment is completed

### trg_before_cancellation_insert
Calculates refund amount before cancellation record is inserted

### trg_before_booking_insert
Prevents booking for past departure dates

### trg_validate_booking_insert
Validates all booking data before insert

### trg_log_payment_changes
Audits all payment status changes

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Railway-Simulation-DBMS-Project.git
   cd Railway-Simulation-DBMS-Project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv zenv
   source zenv/bin/activate  # On Windows: zenv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database**
   ```bash
   createdb railway_db
   ```

5. **Run database schema**
   ```bash
   psql railway_db < database/schema.sql
   psql railway_db < database/views_procedures.sql
   psql railway_db < database/indexes.sql
   psql railway_db < database/seed.sql
   ```

6. **Set up environment variables**
   ```bash
   cp example.env .env
   # Edit .env with your database credentials
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

8. **Access the application**
   Open browser and go to: `http://localhost:5000`

## Usage Examples

### Creating a Booking
```python
# Using the service layer
from app.services.booking_service import BookingService

result = BookingService.create_booking(
    passenger_id=1,
    schedule_id=101,
    seat_id=150,
    fare_amount=2500.00
)

if result['success']:
    print(f"Booking created: {result['booking_id']}")
```

### Getting Revenue Report
```sql
-- SQL query
SELECT * FROM generate_revenue_report('2024-01-01', '2024-01-31');
```

### Processing Cancellation
```sql
-- SQL query
CALL process_cancellation(
    p_booking_id := 1,
    p_staff_id := 5,
    p_reason := 'User requested cancellation',
    p_cancellation_id := NULL
);
```

## Performance Optimization

### Indexes
- Composite index on `bookings(passenger_id, booking_date)`
- Index on `schedules(departure_date, train_id)`
- Index on `seats(coach_id, availability)`
- Index on `payments(payment_status, payment_date)`

### Query Optimization
- Use views for complex joins
- Leverage stored procedures for multi-step operations
- Pagination for large result sets
- Connection pooling for database efficiency

## Error Handling

The application includes comprehensive error handling:
- Database constraints prevent data inconsistency
- Transaction rollback on errors
- Meaningful error messages to users
- Logging of all errors
- HTTP status codes for API responses

## Testing

### Manual Testing Checklist
- [ ] Create passenger and verify data
- [ ] Create train and coaches
- [ ] Create schedules for routes
- [ ] Make bookings and verify seat updates
- [ ] Process payments and verify booking status
- [ ] Cancel bookings and verify refund calculation
- [ ] Check analytics dashboards
- [ ] Test search and filter functionality
- [ ] Verify pagination works
- [ ] Test error cases

### API Testing
Use Postman or curl to test endpoints:
```bash
# Create passenger
curl -X POST http://localhost:5000/api/passengers \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "9876543210",
    "date_of_birth": "1995-05-15",
    "id_proof_type": "CNIC",
    "id_proof_number": "12345-1234567-1"
  }'
```

## Deployment

### Production Considerations
1. Set `DEBUG = False` in config.py
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Set up HTTPS with SSL certificates
4. Configure database backups
5. Implement rate limiting
6. Add request logging and monitoring
7. Set up error tracking (Sentry)

### Docker Deployment
```dockerfile
# Example Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

## Future Enhancements

### Phase 5: Cloud Integration
- Firebase Firestore backup/sync
- Cloud storage for documents
- Real-time notifications

### Phase 6: Advanced Features
- Image uploads for passenger profiles
- PDF ticket generation
- Email confirmations
- SMS notifications

### Phase 7: Analytics
- Dashboard with real-time charts
- Export functionality (CSV, PDF)
- Advanced reporting

### Phase 8: Mobile App
- React Native or Flutter app
- Mobile-optimized booking flow

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support & Contact

For support, issues, or questions:
- Email: support@railway-dbms.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/Railway-Simulation-DBMS-Project/issues)

## Acknowledgments

- PostgreSQL documentation and community
- Flask framework community
- Database design best practices
- Open source contributors

---

**Last Updated**: January 2024
**Project Status**: Active Development
**Version**: 1.0.0
