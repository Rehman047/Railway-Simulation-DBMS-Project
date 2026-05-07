#!/bin/bash
# Database Setup Script
# Run this after configuring .env with your PostgreSQL credentials

set -e

echo "=========================================="
echo "Railway DBMS - Database Setup"
echo "=========================================="
echo

# Source environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
    echo "✓ Environment configuration loaded"
else
    echo "✗ .env file not found. Please copy .env.example to .env and fill in your credentials."
    exit 1
fi

echo

# Test database connection
echo "Testing PostgreSQL connection..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ PostgreSQL connection successful"
else
    echo "✗ Failed to connect to PostgreSQL. Check your credentials in .env"
    exit 1
fi

echo

# Create database if it doesn't exist
echo "Creating database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "  (Database already exists)"
echo "✓ Database ready"

echo

# Run schema
echo "Creating tables..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/schema.sql > /dev/null
echo "✓ Tables created"

# Run seed data
echo "Inserting seed data..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/seed.sql > /dev/null
echo "✓ Seed data inserted"

# Run views and procedures
echo "Creating views, functions, and procedures..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/views_procedures.sql > /dev/null
echo "✓ Advanced features created"

# Run transactions
echo "Creating transaction examples..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/transactions.sql > /dev/null 2>&1 || true
echo "✓ Transaction examples loaded"

echo
echo "=========================================="
echo "✓ Database setup complete!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Start Flask app: python run.py"
echo "3. Access dashboard: http://localhost:5000"
echo
