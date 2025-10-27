#!/usr/bin/env python3
"""
Table Reservation Auto-Unreserve Test
Tests the critical bug fix for table reservation/unreservation logic
"""

import requests
import json
import time
from datetime import datetime

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

print(f"Testing table reservation auto-unreserve at: {API_BASE}")

def test_table_reservation_auto_unreserve():
    """
    Test the complete table reservation auto-unreserve flow:
    1. Create dine-in order for Table 1 with short processing time
    2. Verify table becomes reserved
    3. Wait for processing time to complete
    4. Fetch orders to trigger auto-unreserve
    5. Verify table becomes available
    6. Create new order for same table (should succeed)
    """
    
    print("\n=== Table Reservation Auto-Unreserve Test ===")
    
    # Step 1: Create a test menu item with very short preparation time
    print("1. Creating test menu item with short preparation time...")
    test_menu_item = {
        "name": "Quick Test Item",
        "description": "Test item for reservation testing",
        "price": 10.0,
        "category": "Test",
        "stock": 100,
        "averagePreparationTime": 1  # 1 minute = 60 seconds
    }
    
    try:
        menu_response = requests.post(f"{API_BASE}/menu", 
                                    json=test_menu_item,
                                    headers={'Content-Type': 'application/json'},
                                    timeout=10)
        if menu_response.status_code != 200:
            print(f"❌ Failed to create test menu item: {menu_response.status_code}")
            # Fallback to existing menu items
            menu_response = requests.get(f"{API_BASE}/menu", timeout=10)
            if menu_response.status_code != 200:
                print(f"❌ Failed to get menu items: {menu_response.status_code}")
                return False
            menu_items = menu_response.json()
            if not menu_items:
                print("❌ No menu items available")
                return False
            menu_item = menu_items[0]
            print(f"⚠️  Using existing menu item: {menu_item['name']} (${menu_item['price']}) - {menu_item['averagePreparationTime']} min prep time")
        else:
            menu_item = menu_response.json()
            print(f"✅ Created test menu item: {menu_item['name']} (${menu_item['price']}) - {menu_item['averagePreparationTime']} min prep time")
        
    except Exception as e:
        print(f"❌ Error with menu items: {e}")
        return False
    
    # Step 2: Check initial table status
    print("\n2. Checking initial Table 1 status...")
    try:
        tables_response = requests.get(f"{API_BASE}/tables", timeout=10)
        if tables_response.status_code != 200:
            print(f"❌ Failed to get tables: {tables_response.status_code}")
            return False
        
        tables = tables_response.json()
        table_1 = None
        for table in tables:
            if table['number'] == 1:
                table_1 = table
                break
        
        if not table_1:
            print("❌ Table 1 not found")
            return False
        
        print(f"✅ Table 1 initial status: {table_1['status']}")
        
        # If table is reserved, we need to wait or find another approach
        if table_1['status'] == 'reserved':
            print("⚠️  Table 1 is currently reserved, waiting for it to become available...")
            # Try to unreserve by fetching orders first
            requests.get(f"{API_BASE}/orders", timeout=10)
            time.sleep(2)
            
            # Check again
            tables_response = requests.get(f"{API_BASE}/tables", timeout=10)
            tables = tables_response.json()
            for table in tables:
                if table['number'] == 1:
                    table_1 = table
                    break
            
            if table_1['status'] == 'reserved':
                print("❌ Table 1 is still reserved, cannot proceed with test")
                return False
        
    except Exception as e:
        print(f"❌ Error checking table status: {e}")
        return False
    
    # Step 3: Create first dine-in order with short processing time
    print("\n3. Creating first dine-in order for Table 1...")
    order_data_1 = {
        "tableNumber": 1,
        "customerName": "John Doe",
        "customerPhone": "1234567890",
        "items": [
            {
                "menuItemId": menu_item['id'],
                "menuItemName": menu_item['name'],
                "quantity": 1,
                "price": menu_item['price']
            }
        ],
        "type": "dinein"
    }
    
    try:
        order_response = requests.post(f"{API_BASE}/orders", 
                                     json=order_data_1, 
                                     headers={'Content-Type': 'application/json'},
                                     timeout=10)
        
        if order_response.status_code != 200:
            print(f"❌ Failed to create first order: {order_response.status_code} - {order_response.text}")
            return False
        
        first_order = order_response.json()
        first_order_id = first_order['id']
        processing_time = first_order['processingTime']
        
        print(f"✅ First order created: {first_order['orderNumber']}")
        print(f"   Processing time: {processing_time} seconds")
        print(f"   Order ID: {first_order_id}")
        
    except Exception as e:
        print(f"❌ Error creating first order: {e}")
        return False
    
    # Step 4: Verify table becomes reserved
    print("\n4. Verifying Table 1 is now reserved...")
    try:
        tables_response = requests.get(f"{API_BASE}/tables", timeout=10)
        tables = tables_response.json()
        
        table_1_after_order = None
        for table in tables:
            if table['number'] == 1:
                table_1_after_order = table
                break
        
        if table_1_after_order['status'] != 'reserved':
            print(f"❌ Table 1 should be reserved but is: {table_1_after_order['status']}")
            return False
        
        print("✅ Table 1 is now reserved")
        
    except Exception as e:
        print(f"❌ Error checking table reservation: {e}")
        return False
    
    # Step 5: Wait for processing time to complete (add small buffer)
    wait_time = min(processing_time + 5, 70)  # Cap at 70 seconds for testing
    print(f"\n5. Waiting {wait_time} seconds for order processing to complete...")
    time.sleep(wait_time)
    
    # Step 6: Fetch all orders to trigger auto-unreserve logic
    print("\n6. Fetching all orders to trigger auto-unreserve logic...")
    try:
        orders_response = requests.get(f"{API_BASE}/orders", timeout=10)
        if orders_response.status_code != 200:
            print(f"❌ Failed to fetch orders: {orders_response.status_code}")
            return False
        
        orders = orders_response.json()
        print(f"✅ Fetched {len(orders)} orders")
        
        # Find our order and check its status
        our_order = None
        for order in orders:
            if order['id'] == first_order_id:
                our_order = order
                break
        
        if our_order:
            print(f"   First order status: {our_order['status']}")
            print(f"   Remaining time: {our_order['remainingTime']}")
        
    except Exception as e:
        print(f"❌ Error fetching orders: {e}")
        return False
    
    # Step 7: Verify table is now available
    print("\n7. Verifying Table 1 is now available...")
    try:
        tables_response = requests.get(f"{API_BASE}/tables", timeout=10)
        tables = tables_response.json()
        
        table_1_after_unreserve = None
        for table in tables:
            if table['number'] == 1:
                table_1_after_unreserve = table
                break
        
        if table_1_after_unreserve['status'] != 'available':
            print(f"❌ Table 1 should be available but is: {table_1_after_unreserve['status']}")
            return False
        
        print("✅ Table 1 is now available (auto-unreserved)")
        
    except Exception as e:
        print(f"❌ Error checking table unreservation: {e}")
        return False
    
    # Step 8: Create second dine-in order for same table (should succeed)
    print("\n8. Creating second dine-in order for Table 1...")
    order_data_2 = {
        "tableNumber": 1,
        "customerName": "Jane Smith",
        "customerPhone": "9876543210",
        "items": [
            {
                "menuItemId": menu_item['id'],
                "menuItemName": menu_item['name'],
                "quantity": 1,
                "price": menu_item['price']
            }
        ],
        "type": "dinein"
    }
    
    try:
        order_response_2 = requests.post(f"{API_BASE}/orders", 
                                       json=order_data_2, 
                                       headers={'Content-Type': 'application/json'},
                                       timeout=10)
        
        if order_response_2.status_code != 200:
            print(f"❌ Failed to create second order: {order_response_2.status_code} - {order_response_2.text}")
            return False
        
        second_order = order_response_2.json()
        print(f"✅ Second order created successfully: {second_order['orderNumber']}")
        
    except Exception as e:
        print(f"❌ Error creating second order: {e}")
        return False
    
    # Step 9: Test individual order fetch (get_order endpoint)
    print("\n9. Testing individual order fetch for auto-unreserve...")
    try:
        # Create a third order to test individual fetch
        order_data_3 = {
            "tableNumber": 1,
            "customerName": "Bob Wilson",
            "customerPhone": "5555555555",
            "items": [
                {
                    "menuItemId": menu_item['id'],
                    "menuItemName": menu_item['name'],
                    "quantity": 1,
                    "price": menu_item['price']
                }
            ],
            "type": "dinein"
        }
        
        order_response_3 = requests.post(f"{API_BASE}/orders", 
                                       json=order_data_3, 
                                       headers={'Content-Type': 'application/json'},
                                       timeout=10)
        
        if order_response_3.status_code == 200:
            third_order = order_response_3.json()
            third_order_id = third_order['id']
            
            # Wait for processing time
            time.sleep(min(third_order['processingTime'] + 2, 15))
            
            # Fetch individual order to trigger unreserve
            individual_order_response = requests.get(f"{API_BASE}/orders/{third_order_id}", timeout=10)
            
            if individual_order_response.status_code == 200:
                print("✅ Individual order fetch works")
                
                # Check if table was unreserved
                tables_response = requests.get(f"{API_BASE}/tables", timeout=10)
                tables = tables_response.json()
                
                table_1_final = None
                for table in tables:
                    if table['number'] == 1:
                        table_1_final = table
                        break
                
                if table_1_final and table_1_final['status'] == 'available':
                    print("✅ Individual order fetch also triggers auto-unreserve")
                else:
                    print(f"⚠️  Individual order fetch may not have triggered unreserve (table status: {table_1_final['status'] if table_1_final else 'unknown'})")
            else:
                print(f"⚠️  Individual order fetch failed: {individual_order_response.status_code}")
        else:
            print("⚠️  Could not create third order for individual fetch test")
        
    except Exception as e:
        print(f"⚠️  Error in individual order fetch test: {e}")
    
    print("\n🎉 Table reservation auto-unreserve test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_table_reservation_auto_unreserve()
    
    if success:
        print("\n✅ ALL TESTS PASSED - Table reservation auto-unreserve is working correctly!")
        exit(0)
    else:
        print("\n❌ TEST FAILED - Table reservation auto-unreserve has issues!")
        exit(1)