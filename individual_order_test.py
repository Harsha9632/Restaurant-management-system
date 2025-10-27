#!/usr/bin/env python3
"""
Test individual order fetch auto-unreserve functionality
"""

import requests
import time

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
API_BASE = f"{BASE_URL}/api"

def test_individual_order_unreserve():
    """Test that fetching individual orders also triggers auto-unreserve"""
    
    print("=== Testing Individual Order Fetch Auto-Unreserve ===")
    
    # Get our test menu item
    menu_response = requests.get(f"{API_BASE}/menu", timeout=10)
    menu_items = menu_response.json()
    test_item = None
    for item in menu_items:
        if item['name'] == 'Quick Test Item':
            test_item = item
            break
    
    if not test_item:
        print("❌ Test menu item not found")
        return False
    
    # Create order for Table 1
    order_data = {
        "tableNumber": 1,
        "customerName": "Individual Test User",
        "customerPhone": "1111111111",
        "items": [
            {
                "menuItemId": test_item['id'],
                "menuItemName": test_item['name'],
                "quantity": 1,
                "price": test_item['price']
            }
        ],
        "type": "dinein"
    }
    
    # Create order
    order_response = requests.post(f"{API_BASE}/orders", 
                                 json=order_data, 
                                 headers={'Content-Type': 'application/json'},
                                 timeout=10)
    
    if order_response.status_code != 200:
        print(f"❌ Failed to create order: {order_response.status_code}")
        return False
    
    order = order_response.json()
    order_id = order['id']
    processing_time = order['processingTime']
    
    print(f"✅ Created order {order['orderNumber']} with {processing_time}s processing time")
    
    # Verify table is reserved
    tables_response = requests.get(f"{API_BASE}/tables", timeout=10)
    tables = tables_response.json()
    table_1 = next((t for t in tables if t['number'] == 1), None)
    
    if not table_1 or table_1['status'] != 'reserved':
        print(f"❌ Table 1 should be reserved but is: {table_1['status'] if table_1 else 'not found'}")
        return False
    
    print("✅ Table 1 is reserved")
    
    # Wait for processing time to complete
    wait_time = processing_time + 5
    print(f"⏳ Waiting {wait_time} seconds for processing to complete...")
    time.sleep(wait_time)
    
    # Fetch individual order (this should trigger unreserve)
    individual_response = requests.get(f"{API_BASE}/orders/{order_id}", timeout=10)
    
    if individual_response.status_code != 200:
        print(f"❌ Failed to fetch individual order: {individual_response.status_code}")
        return False
    
    fetched_order = individual_response.json()
    print(f"✅ Fetched individual order - Status: {fetched_order['status']}, Remaining: {fetched_order['remainingTime']}s")
    
    # Check if table is now available
    tables_response = requests.get(f"{API_BASE}/tables", timeout=10)
    tables = tables_response.json()
    table_1_after = next((t for t in tables if t['number'] == 1), None)
    
    if not table_1_after:
        print("❌ Table 1 not found after individual fetch")
        return False
    
    if table_1_after['status'] != 'available':
        print(f"❌ Table 1 should be available after individual fetch but is: {table_1_after['status']}")
        return False
    
    print("✅ Table 1 is now available after individual order fetch")
    
    return True

if __name__ == "__main__":
    success = test_individual_order_unreserve()
    
    if success:
        print("\n🎉 Individual order fetch auto-unreserve test PASSED!")
    else:
        print("\n❌ Individual order fetch auto-unreserve test FAILED!")