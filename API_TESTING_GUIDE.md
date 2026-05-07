# API Testing Guide

## Test Environment Setup

```bash
# Start application
python run.py

# Application runs on: http://localhost:5000
# API Base URL: http://localhost:5000/api
```

## Authentication

All admin endpoints require authentication. Set up a test admin account first.

## Passenger Endpoints

### List Passengers
```bash
curl -X GET "http://localhost:5000/api/passengers?page=1&limit=20"
```

Expected: `200 OK` with pagination metadata

### Create Passenger
```bash
curl -X POST "http://localhost:5000/api/passengers" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "+91-9876543210",
    "address": "123 Main St"
  }'
```

Expected: `201 Created` with passenger ID

### Get Passenger
```bash
curl -X GET "http://localhost:5000/api/passengers/1"
```

Expected: `200 OK` with passenger data

### Update Passenger
```bash
curl -X PUT "http://localhost:5000/api/passengers/1" \
  -H "Content-Type: application/json" \
  -d '{"email": "newemail@example.com"}'
```

Expected: `200 OK` with update confirmation

### Delete Passenger
```bash
curl -X DELETE "http://localhost:5000/api/passengers/1"
```

Expected: `200 OK`

## Train Endpoints

### List Trains
```bash
curl -X GET "http://localhost:5000/api/trains?page=1&limit=20&status=active"
```

### Create Train
```bash
curl -X POST "http://localhost:5000/api/trains" \
  -H "Content-Type: application/json" \
  -d '{
    "train_name": "Express-101",
    "train_number": "EX001",
    "train_type": "Express",
    "capacity": 500,
    "total_coaches": 10,
    "status": "active"
  }'
```

Expected: `201 Created`

### Get Train
```bash
curl -X GET "http://localhost:5000/api/trains/1"
```

## Booking Endpoints

### Create Booking
```bash
curl -X POST "http://localhost:5000/api/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "passenger_id": 1,
    "schedule_id": 5,
    "seat_id": 12,
    "fare_amount": 500.00
  }'
```

Expected: `201 Created` with booking ID

### Get Available Seats
```bash
curl -X GET "http://localhost:5000/api/bookings/available-seats/5"
```

Expected: `200 OK` with available seats list

### List Bookings
```bash
curl -X GET "http://localhost:5000/api/bookings?page=1&limit=20&status=confirmed"
```

### Cancel Booking
```bash
curl -X POST "http://localhost:5000/api/bookings/1/cancel" \
  -H "Content-Type: application/json" \
  -d '{"reason": "User request", "staff_id": 1}'
```

Expected: `200 OK`

## Schedule Endpoints

### List Schedules
```bash
curl -X GET "http://localhost:5000/api/schedules?page=1&limit=20"
```

### Create Schedule
```bash
curl -X POST "http://localhost:5000/api/schedules" \
  -H "Content-Type: application/json" \
  -d '{
    "train_id": 1,
    "route_id": 2,
    "departure_date": "2024-06-15",
    "departure_time": "10:30",
    "arrival_time": "14:45"
  }'
```

Expected: `201 Created`

### Get Schedule
```bash
curl -X GET "http://localhost:5000/api/schedules/1"
```

## Payment Endpoints

### List Payments
```bash
curl -X GET "http://localhost:5000/api/payments?page=1&limit=20"
```

### Record Payment
```bash
curl -X POST "http://localhost:5000/api/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "amount": 500.00,
    "method": "Card"
  }'
```

Expected: `201 Created`

### Get Revenue Summary
```bash
curl -X GET "http://localhost:5000/api/payments/revenue/summary?from_date=2024-01-01&to_date=2024-06-30"
```

## Analytics Endpoints

### Dashboard Summary
```bash
curl -X GET "http://localhost:5000/api/analytics/dashboard"
```

Expected: Key metrics for dashboard

### Revenue by Train
```bash
curl -X GET "http://localhost:5000/api/analytics/revenue/by-train?from_date=2024-01-01&to_date=2024-06-30"
```

### Revenue by Route
```bash
curl -X GET "http://localhost:5000/api/analytics/revenue/by-route?from_date=2024-01-01&to_date=2024-06-30"
```

### Occupancy Rate
```bash
curl -X GET "http://localhost:5000/api/analytics/occupancy?from_date=2024-01-01&to_date=2024-06-30"
```

### Top Routes
```bash
curl -X GET "http://localhost:5000/api/analytics/top-routes?limit=10"
```

### Booking Trends
```bash
curl -X GET "http://localhost:5000/api/analytics/booking-trends?from_date=2024-01-01&to_date=2024-06-30"
```

## Station Endpoints

### List Stations
```bash
curl -X GET "http://localhost:5000/api/stations?page=1&limit=20&city=Lahore"
```

### Create Station
```bash
curl -X POST "http://localhost:5000/api/stations" \
  -H "Content-Type: application/json" \
  -d '{
    "station_name": "Central Station",
    "city": "Lahore",
    "state": "Punjab",
    "address": "123 Station Rd",
    "contact_number": "+92-42-1234567"
  }'
```

### Get Station Services
```bash
curl -X GET "http://localhost:5000/api/stations/1/services"
```

## Routes Between Stations
```bash
curl -X GET "http://localhost:5000/api/stations/routes/between/1/5"
```

## Backup Endpoints

### Create Firestore Backup
```bash
curl -X POST "http://localhost:5000/api/backups/create-firestore" \
  -H "Authorization: Bearer admin-token"
```

Expected: `201 Created` with backup metadata

### Create Local Backup
```bash
curl -X POST "http://localhost:5000/api/backups/create-local" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/backups/backup_2024.json"}'
```

### Auto Backup
```bash
curl -X POST "http://localhost:5000/api/backups/auto-backup"
```

### Get Backup History
```bash
curl -X GET "http://localhost:5000/api/backups/history"
```

### Get Backup Info
```bash
curl -X GET "http://localhost:5000/api/backups/info"
```

## File Storage Endpoints

### Upload Passenger Image
```bash
curl -X POST "http://localhost:5000/api/storage/upload/passenger/1" \
  -F "file=@/path/to/image.jpg"
```

Expected: `201 Created` with file URL

### Upload Train Image
```bash
curl -X POST "http://localhost:5000/api/storage/upload/train/1" \
  -F "file=@/path/to/train.jpg"
```

### Upload Station Image
```bash
curl -X POST "http://localhost:5000/api/storage/upload/station/1" \
  -F "file=@/path/to/station.jpg"
```

### Get File
```bash
curl -X GET "http://localhost:5000/api/storage/file/passenger/1"
```

### Storage Usage
```bash
curl -X GET "http://localhost:5000/api/storage/usage"
```

## Validation Checklist

### Database Operations
- [ ] Schema created successfully
- [ ] Seed data inserted
- [ ] Indexes created
- [ ] Views and procedures working

### API Functionality
- [ ] All CRUD endpoints working
- [ ] Pagination working
- [ ] Filtering working
- [ ] Error handling correct

### Business Logic
- [ ] Bookings prevent double-booking
- [ ] Refunds calculated correctly
- [ ] Occupancy rates accurate
- [ ] Revenue calculations correct

### Authentication & Authorization
- [ ] Admin endpoints protected
- [ ] Role-based access working
- [ ] Session management working
- [ ] Error responses correct

### File Operations
- [ ] File upload working
- [ ] File size limits enforced
- [ ] File type validation working
- [ ] Cloud storage synced

### Backup & Recovery
- [ ] Firestore backup working
- [ ] Local backup working
- [ ] Restore functionality working
- [ ] Backup history tracked

## Common Issues & Solutions

### 404 Not Found
- Check API endpoint URL
- Verify resource ID exists
- Check HTTP method (GET vs POST)

### 400 Bad Request
- Validate JSON structure
- Check required fields
- Verify data types

### 500 Internal Server Error
- Check database connection
- Review server logs
- Verify credentials

### Connection Timeout
- Check database running
- Verify network connectivity
- Check firewall rules

## Performance Testing

### Load Test
```bash
ab -n 1000 -c 10 http://localhost:5000/api/passengers
```

### Response Time Check
```bash
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/analytics/dashboard
```

## Security Testing

### SQL Injection Test
```bash
curl -X GET "http://localhost:5000/api/passengers/1' OR '1'='1"
```

Expected: 404 (should not execute SQL)

### XSS Test
```bash
curl -X POST "http://localhost:5000/api/passengers" \
  -d '{"first_name": "<script>alert(1)</script>"}'
```

Expected: Sanitized or rejected

## Final Sign-Off

- [ ] All endpoints tested
- [ ] All CRUD operations verified
- [ ] Error handling working
- [ ] Performance acceptable
- [ ] Security checks passed
- [ ] Documentation complete
