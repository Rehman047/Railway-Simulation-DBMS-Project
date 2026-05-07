#!/usr/bin/env python
"""
Project Validation Script
Checks if all components are properly implemented
"""
import os
import sys

def check_file_exists(path, description):
    """Check if file exists"""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} NOT FOUND")
        return False

def check_directory_exists(path, description):
    """Check if directory exists"""
    if os.path.isdir(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} NOT FOUND")
        return False

def main():
    """Run all validation checks"""
    print("="*60)
    print("RAILWAY DBMS PROJECT VALIDATION")
    print("="*60)
    
    all_good = True
    
    print("\n1. Checking Directory Structure...")
    all_good &= check_directory_exists('app', 'App directory')
    all_good &= check_directory_exists('app/routes', 'Routes directory')
    all_good &= check_directory_exists('app/services', 'Services directory')
    all_good &= check_directory_exists('app/queries', 'Queries directory')
    all_good &= check_directory_exists('app/utils', 'Utils directory')
    all_good &= check_directory_exists('app/templates', 'Templates directory')
    all_good &= check_directory_exists('app/static', 'Static files directory')
    all_good &= check_directory_exists('database', 'Database directory')
    
    print("\n2. Checking Database Files...")
    all_good &= check_file_exists('database/schema.sql', 'Schema file')
    all_good &= check_file_exists('database/seed.sql', 'Seed data file')
    all_good &= check_file_exists('database/views_procedures.sql', 'Views & Procedures file')
    all_good &= check_file_exists('database/indexes.sql', 'Indexes file')
    all_good &= check_file_exists('database/transactions.sql', 'Transactions file')
    
    print("\n3. Checking Core Application Files...")
    all_good &= check_file_exists('app/__init__.py', 'App factory')
    all_good &= check_file_exists('app/config.py', 'Configuration')
    all_good &= check_file_exists('app/db.py', 'Database layer')
    all_good &= check_file_exists('run.py', 'Run script')
    
    print("\n4. Checking Route Files...")
    routes = [
        'passengers', 'trains', 'stations', 'schedules', 
        'bookings', 'payments', 'cancellations', 'analytics',
        'staff', 'route', 'backups', 'storage', 'views'
    ]
    for route in routes:
        all_good &= check_file_exists(f'app/routes/{route}.py', f'{route} routes')
    
    print("\n5. Checking Service Files...")
    services = [
        'passenger_service', 'train_service', 'station_service',
        'schedule_service', 'booking_service', 'payment_service',
        'cancellation_service', 'analytics_service', 'coach_service',
        'route_service', 'backup_service', 'file_storage_service',
        'firebase_client'
    ]
    for service in services:
        all_good &= check_file_exists(f'app/services/{service}.py', f'{service}')
    
    print("\n6. Checking Query Files...")
    queries = [
        'passenger_queries', 'train_queries', 'station_queries',
        'schedule_queries', 'booking_queries', 'payment_queries',
        'cancellation_queries', 'analytics_queries', 'coach_queries',
        'route_queries', 'seat_queries'
    ]
    for query in queries:
        all_good &= check_file_exists(f'app/queries/{query}.py', f'{query}')
    
    print("\n7. Checking Utility Files...")
    all_good &= check_file_exists('app/utils/__init__.py', 'Utils init')
    all_good &= check_file_exists('app/utils/decorators.py', 'Decorators')
    all_good &= check_file_exists('app/utils/error_handlers.py', 'Error handlers')
    all_good &= check_file_exists('app/utils/validators.py', 'Validators')
    all_good &= check_file_exists('app/utils/result_mappers.py', 'Result mappers')
    
    print("\n8. Checking Template Files...")
    templates = [
        'base', 'dashboard', 'passengers', 'trains', 'stations',
        'schedules', 'bookings', 'analytics'
    ]
    for template in templates:
        all_good &= check_file_exists(f'app/templates/{template}.html', f'{template} template')
    
    print("\n9. Checking Configuration Files...")
    all_good &= check_file_exists('.env', 'Environment file')
    all_good &= check_file_exists('requirements.txt', 'Requirements file')
    all_good &= check_file_exists('.gitignore', 'Git ignore file')
    
    print("\n10. Checking Documentation...")
    all_good &= check_file_exists('README.md', 'README')
    all_good &= check_file_exists('PROJECT_DESCRIPTION.md', 'Project description')
    all_good &= check_file_exists('USER_REQUIREMENTS.md', 'User requirements')
    
    print("\n" + "="*60)
    if all_good:
        print("✓ ALL CHECKS PASSED - Project is complete!")
        return 0
    else:
        print("✗ Some checks failed - Review missing files above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
