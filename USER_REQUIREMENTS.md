# User Roles & Requirements

## Overview
The Railway Simulation DBMS supports multiple user roles, each with specific permissions and responsibilities within the system.

## User Roles

### 1. Admin User (System Administrator)

**Responsibilities:**
- Full system access
- Staff management
- System configuration
- Data backup and recovery
- User access control

**Permissions:**
- ✅ View all entities (trains, stations, passengers, etc.)
- ✅ Create/Edit/Delete all entities
- ✅ Manage staff accounts
- ✅ Access analytics dashboard
- ✅ Export data and reports
- ✅ Configure system settings
- ✅ View audit logs
- ✅ Process bulk operations

**Features:**
- Complete dashboard access
- Staff management interface
- System health monitoring
- Backup and restore functionality
- Activity logging and audit trails

---

### 2. Booking Agent

**Responsibilities:**
- Manage passenger bookings
- Process payments
- Handle cancellations
- Assist passengers

**Permissions:**
- ✅ View passengers (read-only)
- ✅ Create bookings
- ✅ Modify bookings (seat changes)
- ✅ Cancel bookings and process refunds
- ✅ Process payments
- ✅ View payment history
- ✅ Access basic analytics
- ❌ Cannot delete entities
- ❌ Cannot modify trains or schedules
- ❌ Cannot manage staff

**Features:**
- Search passenger database
- Available seat selection
- Booking creation interface
- Payment processing form
- Refund calculator
- Booking cancellation interface
- Agent performance dashboard

**Workflow:**
1. Passenger walks in or calls
2. Agent searches passenger in database
3. Agent selects train schedule and seats
4. System calculates fare
5. Passenger pays (cash/card/online)
6. Booking confirmed
7. Agent can help with cancellations later

---

### 3. Passenger/Customer

**Responsibilities:**
- Make bookings
- View booking history
- Manage profile

**Permissions:**
- ✅ View own profile
- ✅ Search schedules and available trains
- ✅ Make bookings
- ✅ View own bookings
- ✅ View own payment history
- ✅ Request cancellations
- ❌ Cannot view other passengers
- ❌ Cannot modify bookings
- ❌ Cannot access admin features

**Features:**
- Personal dashboard
- Schedule search interface
- Booking confirmation page
- Ticket/Receipt viewing
- Cancellation request
- Payment history
- Profile management

**Typical Flow:**
1. View available trains for route/date
2. Select schedule and seats
3. View fare summary
4. Complete payment
5. Download ticket
6. View booking status anytime

---

### 4. Finance/Accounts User

**Responsibilities:**
- Revenue tracking
- Payment processing
- Refund management
- Financial reporting

**Permissions:**
- ✅ View all payments
- ✅ View revenue reports
- ✅ Process refunds
- ✅ View refund history
- ✅ Access financial analytics
- ✅ Export financial reports
- ✅ View transaction logs
- ❌ Cannot create/edit trains or schedules
- ❌ Cannot delete bookings

**Features:**
- Revenue dashboard
- Payment verification interface
- Refund processing form
- Financial reports
- Transaction history
- Export to Excel/PDF

**Reports Access:**
- Daily revenue report
- Weekly/Monthly revenue trends
- Revenue by route
- Payment method analysis
- Refund statistics
- Customer payment status

---

### 5. Operations Manager

**Responsibilities:**
- Train and schedule management
- Route optimization
- Occupancy monitoring

**Permissions:**
- ✅ View all trains, stations, schedules
- ✅ Create/Edit trains
- ✅ Create/Edit schedules
- ✅ Create routes
- ✅ View occupancy statistics
- ✅ View bookings (read-only)
- ✅ Access operations analytics
- ❌ Cannot delete trains or schedules
- ❌ Cannot process payments
- ❌ Cannot manage staff

**Features:**
- Train management dashboard
- Schedule creation interface
- Occupancy monitoring
- Route management
- Capacity planning tools
- Operations analytics

**Responsibilities:**
1. Add new trains to the system
2. Create schedules for trains
3. Monitor occupancy in real-time
4. Plan peak/off-peak schedules
5. Manage route changes
6. Monitor schedule compliance

---

### 6. Station Manager

**Responsibilities:**
- Station operations
- Service management
- Platform coordination

**Permissions:**
- ✅ View station details
- ✅ Update station information
- ✅ Manage station services
- ✅ View schedules (read-only)
- ✅ View arriving trains
- ✅ Access station analytics
- ❌ Cannot create new stations
- ❌ Cannot delete entities

**Features:**
- Station dashboard
- Service management
- Incoming trains view
- Platform assignment
- Passenger announcements
- Station analytics

---

### 7. Data Analyst

**Responsibilities:**
- Generate reports
- Analyze trends
- Business intelligence

**Permissions:**
- ✅ View all data (read-only)
- ✅ Access all analytics
- ✅ Export data
- ✅ Generate custom reports
- ✅ View historical data
- ❌ Cannot create/modify/delete any entity

**Features:**
- Advanced analytics dashboard
- Report builder
- Data export tools
- Visualization dashboard
- Trend analysis
- Forecasting tools

---

## Use Cases & Scenarios

### Scenario 1: New Passenger Booking

**Actor**: Booking Agent

**Steps**:
1. Agent selects "New Booking"
2. Searches/Creates passenger record
3. Enters passenger details
4. Searches for trains on specific route/date
5. System displays available trains with fares
6. Agent selects train and seats
7. System calculates total fare
8. Passenger provides payment
9. Agent confirms booking
10. System generates ticket

**Expected Result**: Booking confirmed, seat marked as booked, payment recorded

---

### Scenario 2: Passenger Cancellation

**Actor**: Passenger or Booking Agent

**Steps**:
1. Passenger/Agent requests cancellation
2. System searches for booking
3. System checks cancellation policy (days before departure)
4. System calculates refund amount based on policy
5. Admin approves refund (if required)
6. Refund processed
7. Booking marked as cancelled
8. Seat marked as available

**Expected Result**: Booking cancelled, refund processed, seat released

---

### Scenario 3: Revenue Analysis

**Actor**: Finance User or Analyst

**Steps**:
1. User accesses Analytics Dashboard
2. Selects date range
3. Selects metrics (revenue, bookings, occupancy)
4. System generates report
5. User can view trends and exports data

**Expected Result**: Comprehensive revenue report with visualizations

---

### Scenario 4: Schedule Management

**Actor**: Operations Manager

**Steps**:
1. Manager logs in to system
2. Selects "Manage Schedules"
3. Can view all schedules
4. Can add new schedule for train-route-date
5. System validates train availability
6. Schedule created with initial seat availability
7. Seats marked as available

**Expected Result**: New schedule created, seats initialized

---

## Access Control Matrix

| Feature | Admin | Agent | Passenger | Finance | Operations | Station | Analyst |
|---------|-------|-------|-----------|---------|-----------|---------|---------|
| View Trains | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Create Trains | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| View Passengers | ✅ | ✅ | 🔒 Own Only | ✅ | ❌ | ❌ | ✅ |
| Create Booking | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Cancel Booking | ✅ | ✅ | 🔒 Own Only | ✅ | ❌ | ❌ | ❌ |
| Process Payment | ✅ | ✅ | 🔒 Own Only | ✅ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | 🔒 Own Data | ✅ | ✅ | ✅ | ✅ |
| Process Refund | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Manage Staff | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |

Legend:
- ✅ Full Access
- ❌ No Access  
- 🔒 Restricted (own data only)

---

## System Requirements

### For All Users
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Stable internet connection
- Valid login credentials

### For Booking Agents
- Access to booking terminal
- Payment processing device (if handling cash/card)
- Customer communication tools

### For Administrators
- Advanced system access
- Server/Database knowledge
- Understanding of system architecture

### For Analysts
- Data analysis skills
- Understanding of SQL queries
- Report generation tools

---

## Training Requirements

### Admin Training
- System architecture
- Database concepts
- User management
- Backup and recovery
- Security policies

### Booking Agent Training
- Booking process
- Payment handling
- Customer service
- Cancellation policies
- Refund calculations
- System navigation

### Passenger Training
- Self-service booking
- Payment methods
- Ticket viewing
- Cancellation requests
- FAQ assistance

### Finance Training
- Revenue tracking
- Payment verification
- Refund processing
- Report generation
- Audit procedures

### Operations Training
- Train management
- Schedule creation
- Capacity planning
- Route management

---

## Support & Help

### For Passengers
- Help desk: +91-XXXX-XXXX-XXX
- Email: support@railway-system.com
- Live chat on website
- FAQ section

### For Agents/Managers
- Technical support: support@railway-system.com
- Training materials: On-system help
- Supervisor escalation for complex issues

### For Administrators
- System documentation
- Database documentation
- API documentation
- Community forums

---

**Document Version**: 1.0.0
**Last Updated**: January 2024
