#!/usr/bin/env python3
"""
Backend API Testing for Restaurant Management System
Tests Analytics, Tables, Menu Items, and Orders APIs
"""

import requests
import json
import os
from datetime import datetime
import random
import string

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get REACT_APP_BACKEND_URL from frontend/.env")
    exit(1)

API_BASE = f"{BASE_URL}/api"

print(f"Testing backend APIs at: {API_BASE}")

# Test data generators
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_phone():
    return f"+1{random.randint(1000000000, 9999999999)}"

# Test results tracking
test_results = {
    'analytics': {'passed': 0, 'failed': 0, 'errors': []},
    'tables': {'passed': 0, 'failed': 0, 'errors': []},
    'menu': {'passed': 0, 'failed': 0, 'errors': []},
    'orders': {'passed': 0, 'failed': 0, 'errors': []}
}

def log_test_result(category, test_name, success, error_msg=None):
    if success:
        test_results[category]['passed'] += 1
        print(f"✅ {test_name}")
    else:
        test_results[category]['failed'] += 1
        test_results[category]['errors'].append(f"{test_name}: {error_msg}")
        print(f"❌ {test_name}: {error_msg}")

def test_analytics_api():
    """Test Analytics API endpoint"""
    print("\n=== Testing Analytics API ===")
    
    try:
        response = requests.get(f"{API_BASE}/analytics", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ['totalChefs', 'totalRevenue', 'totalOrders', 'totalClients', 
                             'ordersByType', 'revenueByDay', 'chefOrderDistribution']
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                log_test_result('analytics', 'Analytics API structure', False, 
                              f"Missing fields: {missing_fields}")
                return
            
            # Validate ordersByType structure
            orders_by_type = data['ordersByType']
            expected_types = ['dinein', 'takeaway', 'served']
            missing_types = [t for t in expected_types if t not in orders_by_type]
            if missing_types:
                log_test_result('analytics', 'Analytics ordersByType structure', False,
                              f"Missing order types: {missing_types}")
            else:
                log_test_result('analytics', 'Analytics ordersByType structure', True)
            
            # Validate revenueByDay structure
            revenue_by_day = data['revenueByDay']
            if isinstance(revenue_by_day, list):
                if revenue_by_day:  # If there's data, check structure
                    sample_day = revenue_by_day[0]
                    if 'day' in sample_day and 'revenue' in sample_day:
                        log_test_result('analytics', 'Analytics revenueByDay structure', True)
                    else:
                        log_test_result('analytics', 'Analytics revenueByDay structure', False,
                                      "Missing 'day' or 'revenue' fields")
                else:
                    log_test_result('analytics', 'Analytics revenueByDay structure', True)
            else:
                log_test_result('analytics', 'Analytics revenueByDay structure', False,
                              "revenueByDay should be a list")
            
            # Validate chefOrderDistribution structure
            chef_distribution = data['chefOrderDistribution']
            if isinstance(chef_distribution, list):
                if chef_distribution:  # If there's data, check structure
                    sample_chef = chef_distribution[0]
                    if 'name' in sample_chef and 'orders' in sample_chef:
                        log_test_result('analytics', 'Analytics chefOrderDistribution structure', True)
                    else:
                        log_test_result('analytics', 'Analytics chefOrderDistribution structure', False,
                                      "Missing 'name' or 'orders' fields")
                else:
                    log_test_result('analytics', 'Analytics chefOrderDistribution structure', True)
            else:
                log_test_result('analytics', 'Analytics chefOrderDistribution structure', False,
                              "chefOrderDistribution should be a list")
            
            # Validate data types
            if isinstance(data['totalChefs'], int) and data['totalChefs'] >= 0:
                log_test_result('analytics', 'Analytics totalChefs type', True)
            else:
                log_test_result('analytics', 'Analytics totalChefs type', False,
                              f"totalChefs should be non-negative integer, got {type(data['totalChefs'])}")
            
            if isinstance(data['totalRevenue'], (int, float)) and data['totalRevenue'] >= 0:
                log_test_result('analytics', 'Analytics totalRevenue type', True)
            else:
                log_test_result('analytics', 'Analytics totalRevenue type', False,
                              f"totalRevenue should be non-negative number, got {type(data['totalRevenue'])}")
            
            log_test_result('analytics', 'Analytics API response', True)
            
        else:
            log_test_result('analytics', 'Analytics API response', False, 
                          f"HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        log_test_result('analytics', 'Analytics API connection', False, str(e))
    except Exception as e:
        log_test_result('analytics', 'Analytics API general', False, str(e))

def test_tables_api():
    """Test Tables API CRUD operations"""
    print("\n=== Testing Tables API ===")
    
    created_table_id = None
    
    try:
        # Test GET all tables
        response = requests.get(f"{API_BASE}/tables", timeout=10)
        if response.status_code == 200:
            tables = response.json()
            if isinstance(tables, list):
                log_test_result('tables', 'Tables GET all', True)
                
                # Check table structure if tables exist
                if tables:
                    sample_table = tables[0]
                    required_fields = ['id', 'number', 'chairCount', 'status']
                    missing_fields = [field for field in required_fields if field not in sample_table]
                    if missing_fields:
                        log_test_result('tables', 'Tables structure', False, 
                                      f"Missing fields: {missing_fields}")
                    else:
                        log_test_result('tables', 'Tables structure', True)
                        
                        # Check status values
                        valid_statuses = ['available', 'reserved']
                        if sample_table['status'] in valid_statuses:
                            log_test_result('tables', 'Tables status values', True)
                        else:
                            log_test_result('tables', 'Tables status values', False,
                                          f"Invalid status: {sample_table['status']}")
            else:
                log_test_result('tables', 'Tables GET all', False, "Response should be a list")
        else:
            log_test_result('tables', 'Tables GET all', False, 
                          f"HTTP {response.status_code}: {response.text}")
        
        # Test POST create table
        table_data = {
            "chairCount": 4,
            "name": f"Test Table {generate_random_string(4)}"
        }
        
        response = requests.post(f"{API_BASE}/tables", 
                               json=table_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            created_table = response.json()
            created_table_id = created_table.get('id')
            
            # Validate created table structure
            if all(field in created_table for field in ['id', 'number', 'chairCount', 'status']):
                if created_table['status'] == 'available':
                    log_test_result('tables', 'Tables POST create', True)
                else:
                    log_test_result('tables', 'Tables POST create', False,
                                  f"New table should have 'available' status, got {created_table['status']}")
            else:
                log_test_result('tables', 'Tables POST create', False, "Invalid response structure")
        else:
            log_test_result('tables', 'Tables POST create', False, 
                          f"HTTP {response.status_code}: {response.text}")
        
        # Test DELETE table (if we created one)
        if created_table_id:
            response = requests.delete(f"{API_BASE}/tables/{created_table_id}", timeout=10)
            if response.status_code == 200:
                log_test_result('tables', 'Tables DELETE', True)
            else:
                log_test_result('tables', 'Tables DELETE', False, 
                              f"HTTP {response.status_code}: {response.text}")
        
    except requests.exceptions.RequestException as e:
        log_test_result('tables', 'Tables API connection', False, str(e))
    except Exception as e:
        log_test_result('tables', 'Tables API general', False, str(e))

def test_menu_api():
    """Test Menu Items API"""
    print("\n=== Testing Menu API ===")
    
    try:
        # Test GET menu items
        response = requests.get(f"{API_BASE}/menu", timeout=10)
        if response.status_code == 200:
            menu_items = response.json()
            if isinstance(menu_items, list):
                log_test_result('menu', 'Menu GET all', True)
                
                # Check menu item structure if items exist
                if menu_items:
                    sample_item = menu_items[0]
                    required_fields = ['id', 'name', 'description', 'price', 'category', 'stock', 'averagePreparationTime']
                    missing_fields = [field for field in required_fields if field not in sample_item]
                    if missing_fields:
                        log_test_result('menu', 'Menu item structure', False, 
                                      f"Missing fields: {missing_fields}")
                    else:
                        log_test_result('menu', 'Menu item structure', True)
                        
                        # Validate data types
                        if isinstance(sample_item['price'], (int, float)) and sample_item['price'] > 0:
                            log_test_result('menu', 'Menu item price type', True)
                        else:
                            log_test_result('menu', 'Menu item price type', False,
                                          f"Price should be positive number, got {sample_item['price']}")
            else:
                log_test_result('menu', 'Menu GET all', False, "Response should be a list")
        else:
            log_test_result('menu', 'Menu GET all', False, 
                          f"HTTP {response.status_code}: {response.text}")
        
        # Test GET categories
        response = requests.get(f"{API_BASE}/menu/categories/list", timeout=10)
        if response.status_code == 200:
            categories_data = response.json()
            if 'categories' in categories_data and isinstance(categories_data['categories'], list):
                log_test_result('menu', 'Menu categories', True)
            else:
                log_test_result('menu', 'Menu categories', False, "Invalid categories response structure")
        else:
            log_test_result('menu', 'Menu categories', False, 
                          f"HTTP {response.status_code}: {response.text}")
        
    except requests.exceptions.RequestException as e:
        log_test_result('menu', 'Menu API connection', False, str(e))
    except Exception as e:
        log_test_result('menu', 'Menu API general', False, str(e))

def test_orders_api():
    """Test Orders API"""
    print("\n=== Testing Orders API ===")
    
    try:
        # Test GET orders
        response = requests.get(f"{API_BASE}/orders", timeout=10)
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list):
                log_test_result('orders', 'Orders GET all', True)
                
                # Check order structure if orders exist
                if orders:
                    sample_order = orders[0]
                    required_fields = ['id', 'orderNumber', 'customerName', 'customerPhone', 
                                     'items', 'type', 'status', 'totalAmount', 'grandTotal', 'createdAt']
                    missing_fields = [field for field in required_fields if field not in sample_order]
                    if missing_fields:
                        log_test_result('orders', 'Orders structure', False, 
                                      f"Missing fields: {missing_fields}")
                    else:
                        log_test_result('orders', 'Orders structure', True)
                        
                        # Validate order type
                        valid_types = ['dinein', 'takeaway']
                        if sample_order['type'] in valid_types:
                            log_test_result('orders', 'Orders type values', True)
                        else:
                            log_test_result('orders', 'Orders type values', False,
                                          f"Invalid order type: {sample_order['type']}")
                        
                        # Validate order status
                        valid_statuses = ['processing', 'done', 'completed']
                        if sample_order['status'] in valid_statuses:
                            log_test_result('orders', 'Orders status values', True)
                        else:
                            log_test_result('orders', 'Orders status values', False,
                                          f"Invalid order status: {sample_order['status']}")
            else:
                log_test_result('orders', 'Orders GET all', False, "Response should be a list")
        else:
            log_test_result('orders', 'Orders GET all', False, 
                          f"HTTP {response.status_code}: {response.text}")
        
        # Test order creation (requires menu items to exist)
        # First get menu items to create a valid order
        menu_response = requests.get(f"{API_BASE}/menu", timeout=10)
        if menu_response.status_code == 200:
            menu_items = menu_response.json()
            if menu_items:
                # Create test order with first menu item
                sample_menu_item = menu_items[0]
                order_data = {
                    "customerName": f"Test Customer {generate_random_string(4)}",
                    "customerPhone": generate_phone(),
                    "items": [
                        {
                            "menuItemId": sample_menu_item['id'],
                            "menuItemName": sample_menu_item['name'],
                            "quantity": 2,
                            "price": sample_menu_item['price']
                        }
                    ],
                    "type": "takeaway"
                }
                
                response = requests.post(f"{API_BASE}/orders", 
                                       json=order_data, 
                                       headers={'Content-Type': 'application/json'},
                                       timeout=10)
                
                if response.status_code == 200:
                    created_order = response.json()
                    # Validate created order
                    if all(field in created_order for field in ['id', 'orderNumber', 'status', 'grandTotal']):
                        if created_order['status'] == 'processing':
                            log_test_result('orders', 'Orders POST create', True)
                        else:
                            log_test_result('orders', 'Orders POST create', False,
                                          f"New order should have 'processing' status, got {created_order['status']}")
                    else:
                        log_test_result('orders', 'Orders POST create', False, "Invalid order response structure")
                else:
                    log_test_result('orders', 'Orders POST create', False, 
                                  f"HTTP {response.status_code}: {response.text}")
            else:
                log_test_result('orders', 'Orders POST create', False, "No menu items available for order creation")
        
    except requests.exceptions.RequestException as e:
        log_test_result('orders', 'Orders API connection', False, str(e))
    except Exception as e:
        log_test_result('orders', 'Orders API general', False, str(e))

def print_test_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*60)
    print("BACKEND API TEST SUMMARY")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    critical_failures = []
    
    for category, results in test_results.items():
        passed = results['passed']
        failed = results['failed']
        total_passed += passed
        total_failed += failed
        
        status = "✅ PASS" if failed == 0 else "❌ FAIL"
        print(f"{category.upper():12} | {status} | {passed} passed, {failed} failed")
        
        if failed > 0:
            critical_failures.extend(results['errors'])
    
    print("-" * 60)
    print(f"TOTAL:       | {total_passed} passed, {total_failed} failed")
    
    if critical_failures:
        print("\nCRITICAL FAILURES:")
        for i, error in enumerate(critical_failures, 1):
            print(f"{i}. {error}")
    
    print("\n" + "="*60)
    
    return total_failed == 0

if __name__ == "__main__":
    print("Starting Restaurant Management Backend API Tests...")
    print(f"Backend URL: {API_BASE}")
    
    # Run all tests
    test_analytics_api()
    test_tables_api()
    test_menu_api()
    test_orders_api()
    
    # Print summary
    all_tests_passed = print_test_summary()
    
    if all_tests_passed:
        print("🎉 All backend API tests passed!")
        exit(0)
    else:
        print("⚠️  Some backend API tests failed!")
        exit(1)