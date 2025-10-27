from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================

# Menu Item Models
class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    averagePreparationTime: int  # in minutes
    imageUrl: Optional[str] = None

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    averagePreparationTime: int
    imageUrl: Optional[str] = None

# Table Models
class Table(BaseModel):
    id: str
    number: int
    chairCount: int
    name: Optional[str] = None
    status: str = "available"  # available or reserved
    customerId: Optional[str] = None

class TableCreate(BaseModel):
    chairCount: int
    name: Optional[str] = None

# Order Models
class OrderItem(BaseModel):
    menuItemId: str
    menuItemName: str
    quantity: int
    price: float
    cookingInstructions: Optional[str] = None

class Order(BaseModel):
    id: str
    orderNumber: str
    tableNumber: Optional[int] = None
    customerName: str
    customerPhone: str
    customerAddress: Optional[str] = None
    items: List[OrderItem]
    type: str  # dinein or takeaway
    status: str  # processing, done, completed
    totalAmount: float
    taxes: float
    deliveryCharge: float
    grandTotal: float
    processingTime: int  # in seconds
    remainingTime: int  # in seconds
    createdAt: str
    assignedChef: Optional[str] = None

class OrderCreate(BaseModel):
    tableNumber: Optional[int] = None
    customerName: str
    customerPhone: str
    customerAddress: Optional[str] = None
    items: List[OrderItem]
    type: str  # dinein or takeaway
    cookingInstructions: Optional[str] = None

# Customer Models
class Customer(BaseModel):
    id: str
    name: str
    phone: str
    address: Optional[str] = None
    ordersCount: int = 0

# Chef Models
class Chef(BaseModel):
    id: str
    name: str
    currentOrders: int = 0

class ChefCreate(BaseModel):
    name: str

# Analytics Models
class Analytics(BaseModel):
    totalChefs: int
    totalRevenue: float
    totalOrders: int
    totalClients: int
    ordersByType: dict
    revenueByDay: List[dict]
    chefOrderDistribution: List[dict]

# ==================== UTILITY FUNCTIONS ====================

async def get_next_order_number():
    """Generate next order number"""
    count = await db.orders.count_documents({})
    return f"{count + 108}"

async def get_next_table_number():
    """Get next available table number"""
    tables = await db.tables.find({}).to_list(1000)
    if not tables:
        return 1
    numbers = [t['number'] for t in tables]
    return max(numbers) + 1

async def assign_chef_to_order():
    """Assign order to chef with least orders"""
    chefs = await db.chefs.find({}).to_list(1000)
    if not chefs:
        return None
    
    # Sort by current orders
    chefs_sorted = sorted(chefs, key=lambda x: x['currentOrders'])
    
    # If multiple chefs have same order count, pick randomly
    min_orders = chefs_sorted[0]['currentOrders']
    available_chefs = [c for c in chefs_sorted if c['currentOrders'] == min_orders]
    
    selected_chef = random.choice(available_chefs)
    
    # Increment chef's order count
    await db.chefs.update_one(
        {'id': selected_chef['id']},
        {'$inc': {'currentOrders': 1}}
    )
    
    return selected_chef['name']

async def calculate_order_timing(items):
    """Calculate total preparation time based on items"""
    total_time = 0
    for item in items:
        menu_item = await db.menu_items.find_one({'id': item['menuItemId']})
        if menu_item:
            total_time += menu_item['averagePreparationTime'] * item['quantity']
    return total_time * 60  # Convert to seconds

# ==================== ROUTES ====================

# Menu Routes
@api_router.post("/menu", response_model=MenuItem)
async def create_menu_item(item: MenuItemCreate):
    item_id = f"menu_{datetime.now().timestamp()}"
    item_dict = item.model_dump()
    item_dict['id'] = item_id
    
    await db.menu_items.insert_one(item_dict)
    return MenuItem(**item_dict)

@api_router.get("/menu", response_model=List[MenuItem])
async def get_menu_items(category: Optional[str] = None):
    query = {} if not category else {'category': category}
    items = await db.menu_items.find(query, {'_id': 0}).to_list(1000)
    return items

@api_router.get("/menu/{item_id}", response_model=MenuItem)
async def get_menu_item(item_id: str):
    item = await db.menu_items.find_one({'id': item_id}, {'_id': 0})
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@api_router.put("/menu/{item_id}", response_model=MenuItem)
async def update_menu_item(item_id: str, item: MenuItemCreate):
    item_dict = item.model_dump()
    result = await db.menu_items.update_one(
        {'id': item_id},
        {'$set': item_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    updated_item = await db.menu_items.find_one({'id': item_id}, {'_id': 0})
    return MenuItem(**updated_item)

@api_router.delete("/menu/{item_id}")
async def delete_menu_item(item_id: str):
    result = await db.menu_items.delete_one({'id': item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Menu item deleted successfully"}

@api_router.get("/menu/categories/list")
async def get_categories():
    """Get all unique categories"""
    categories = await db.menu_items.distinct('category')
    return {"categories": categories}

# Table Routes
@api_router.post("/tables", response_model=Table)
async def create_table(table: TableCreate):
    table_number = await get_next_table_number()
    table_id = f"table_{table_number}"
    
    table_dict = table.model_dump()
    table_dict['id'] = table_id
    table_dict['number'] = table_number
    table_dict['status'] = 'available'
    
    await db.tables.insert_one(table_dict)
    return Table(**table_dict)

@api_router.get("/tables", response_model=List[Table])
async def get_tables():
    tables = await db.tables.find({}, {'_id': 0}).sort('number', 1).to_list(1000)
    return tables

@api_router.get("/tables/{table_id}", response_model=Table)
async def get_table(table_id: str):
    table = await db.tables.find_one({'id': table_id}, {'_id': 0})
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@api_router.put("/tables/{table_id}/status")
async def update_table_status(table_id: str, status: str, customer_id: Optional[str] = None):
    """Update table status (available/reserved)"""
    update_data = {'status': status}
    if customer_id:
        update_data['customerId'] = customer_id
    elif status == 'available':
        update_data['customerId'] = None
    
    result = await db.tables.update_one(
        {'id': table_id},
        {'$set': update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Table not found")
    
    updated_table = await db.tables.find_one({'id': table_id}, {'_id': 0})
    return Table(**updated_table)

@api_router.delete("/tables/{table_id}")
async def delete_table(table_id: str):
    # Check if table is reserved
    table = await db.tables.find_one({'id': table_id})
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if table['status'] == 'reserved':
        raise HTTPException(status_code=400, detail="Cannot delete reserved table")
    
    table_number = table['number']
    
    # Delete the table
    await db.tables.delete_one({'id': table_id})
    
    # Renumber remaining tables
    tables = await db.tables.find({'number': {'$gt': table_number}}).sort('number', 1).to_list(1000)
    for t in tables:
        await db.tables.update_one(
            {'id': t['id']},
            {'$set': {'number': t['number'] - 1}}
        )
    
    return {"message": "Table deleted and numbers reshuffled"}

# Order Routes
@api_router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    # CHECK IF TABLE IS RESERVED (if dine-in order)
    if order.type == 'dinein' and order.tableNumber:
        # Check if table exists
        table = await db.tables.find_one({'number': order.tableNumber})
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        # Check if table is already reserved
        if table.get('status') == 'reserved':
            raise HTTPException(status_code=400, detail="Table reserved!!!")
    
    order_number = await get_next_order_number()
    order_id = f"order_{datetime.now().timestamp()}"
    
    # Calculate totals
    item_total = sum(item.price * item.quantity for item in order.items)
    taxes = item_total * 0.05  # 5% tax
    delivery_charge = 50 if order.type == 'takeaway' else 0
    grand_total = item_total + taxes + delivery_charge
    
    # Calculate processing time
    processing_time = await calculate_order_timing([item.model_dump() for item in order.items])
    
    # Assign chef
    assigned_chef = await assign_chef_to_order()
    
    # If dine-in, mark table as reserved
    if order.type == 'dinein' and order.tableNumber:
        await db.tables.update_one(
            {'number': order.tableNumber},
            {'$set': {'status': 'reserved'}}
        )
    
    # Create customer or update
    customer = await db.customers.find_one({'phone': order.customerPhone})
    if customer:
        await db.customers.update_one(
            {'phone': order.customerPhone},
            {'$inc': {'ordersCount': 1}}
        )
    else:
        customer_id = f"customer_{datetime.now().timestamp()}"
        await db.customers.insert_one({
            'id': customer_id,
            'name': order.customerName,
            'phone': order.customerPhone,
            'address': order.customerAddress,
            'ordersCount': 1
        })
    
    order_dict = order.model_dump()
    order_dict['id'] = order_id
    order_dict['orderNumber'] = order_number
    order_dict['status'] = 'processing'
    order_dict['totalAmount'] = item_total
    order_dict['taxes'] = taxes
    order_dict['deliveryCharge'] = delivery_charge
    order_dict['grandTotal'] = grand_total
    order_dict['processingTime'] = processing_time
    order_dict['remainingTime'] = processing_time
    order_dict['createdAt'] = datetime.now(timezone.utc).isoformat()
    order_dict['assignedChef'] = assigned_chef
    
    await db.orders.insert_one(order_dict)
    return Order(**order_dict)

@api_router.get("/orders", response_model=List[Order])
async def get_orders(status: Optional[str] = None, type: Optional[str] = None):
    query = {}
    if status:
        query['status'] = status
    if type:
        query['type'] = type
    
    orders = await db.orders.find(query, {'_id': 0}).sort('createdAt', -1).to_list(1000)
    
    # Update remaining time for each order
    for order in orders:
        if order['status'] == 'processing':
            created_at = datetime.fromisoformat(order['createdAt'])
            elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
            remaining = max(0, order['processingTime'] - int(elapsed))
            order['remainingTime'] = remaining
            
            # Auto-update status if time is up
            if remaining == 0:
                await db.orders.update_one(
                    {'id': order['id']},
                    {'$set': {'status': 'done', 'remainingTime': 0}}
                )
                order['status'] = 'done'
                
                # UNRESERVE TABLE if dine-in order
                if order.get('type') == 'dinein' and order.get('tableNumber'):
                    await db.tables.update_one(
                        {'number': order['tableNumber']},
                        {'$set': {'status': 'available'}}
                    )
        else:
            order['remainingTime'] = 0
    
    return orders

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update remaining time
    if order['status'] == 'processing':
        created_at = datetime.fromisoformat(order['createdAt'])
        elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
        remaining = max(0, order['processingTime'] - int(elapsed))
        order['remainingTime'] = remaining
        
        if remaining == 0:
            await db.orders.update_one(
                {'id': order_id},
                {'$set': {'status': 'done', 'remainingTime': 0}}
            )
            order['status'] = 'done'
            
            # UNRESERVE TABLE if dine-in order
            if order.get('type') == 'dinein' and order.get('tableNumber'):
                await db.tables.update_one(
                    {'number': order['tableNumber']},
                    {'$set': {'status': 'available'}}
                )
    
    return order

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    """Update order status"""
    order = await db.orders.find_one({'id': order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    result = await db.orders.update_one(
        {'id': order_id},
        {'$set': {'status': status}}
    )
    
    # UNRESERVE TABLE when status changes to 'done' (for dine-in)
    if status == 'done' and order['type'] == 'dinein' and order.get('tableNumber'):
        await db.tables.update_one(
            {'number': order['tableNumber']},
            {'$set': {'status': 'available'}}
        )
    
    # If order is completed, additional cleanup
    if status == 'completed':
        # Decrement chef's current orders
        if order.get('assignedChef'):
            await db.chefs.update_one(
                {'name': order['assignedChef']},
                {'$inc': {'currentOrders': -1}}
            )
    
    updated_order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    return Order(**updated_order)

# Customer Routes
@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find({}, {'_id': 0}).to_list(1000)
    return customers

@api_router.get("/customers/{phone}")
async def get_customer_by_phone(phone: str):
    customer = await db.customers.find_one({'phone': phone}, {'_id': 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Chef Routes
@api_router.post("/chefs", response_model=Chef)
async def create_chef(chef: ChefCreate):
    chef_id = f"chef_{datetime.now().timestamp()}"
    chef_dict = chef.model_dump()
    chef_dict['id'] = chef_id
    chef_dict['currentOrders'] = 0
    
    await db.chefs.insert_one(chef_dict)
    return Chef(**chef_dict)

@api_router.get("/chefs", response_model=List[Chef])
async def get_chefs():
    chefs = await db.chefs.find({}, {'_id': 0}).to_list(1000)
    return chefs

@api_router.put("/chefs/{chef_id}", response_model=Chef)
async def update_chef(chef_id: str, chef: ChefCreate):
    chef_dict = chef.model_dump()
    result = await db.chefs.update_one(
        {'id': chef_id},
        {'$set': chef_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chef not found")
    
    updated_chef = await db.chefs.find_one({'id': chef_id}, {'_id': 0})
    return Chef(**updated_chef)

@api_router.delete("/chefs/{chef_id}")
async def delete_chef(chef_id: str):
    result = await db.chefs.delete_one({'id': chef_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chef not found")
    return {"message": "Chef deleted successfully"}

# Analytics Routes
@api_router.get("/analytics", response_model=Analytics)
async def get_analytics():
    # Total chefs
    total_chefs = await db.chefs.count_documents({})
    
    # Total revenue
    orders = await db.orders.find({}, {'_id': 0}).to_list(10000)
    total_revenue = sum(order['grandTotal'] for order in orders)
    
    # Total orders
    total_orders = len(orders)
    
    # Total clients (unique phone numbers)
    total_clients = await db.customers.count_documents({})
    
    # Orders by type
    dinein_orders = len([o for o in orders if o['type'] == 'dinein'])
    takeaway_orders = len([o for o in orders if o['type'] == 'takeaway'])
    served_orders = len([o for o in orders if o['status'] == 'done' or o['status'] == 'completed'])
    
    orders_by_type = {
        'dinein': dinein_orders,
        'takeaway': takeaway_orders,
        'served': served_orders
    }
    
    # Revenue by day of week
    revenue_by_day = {}
    for order in orders:
        created_at = datetime.fromisoformat(order['createdAt'])
        day = created_at.strftime('%a')  # Mon, Tue, etc.
        if day not in revenue_by_day:
            revenue_by_day[day] = 0
        revenue_by_day[day] += order['grandTotal']
    
    revenue_by_day_list = [{'day': day, 'revenue': revenue} for day, revenue in revenue_by_day.items()]
    
    # Chef order distribution
    chefs = await db.chefs.find({}, {'_id': 0}).to_list(1000)
    chef_distribution = []
    for chef in chefs:
        chef_orders = len([o for o in orders if o.get('assignedChef') == chef['name']])
        chef_distribution.append({'name': chef['name'], 'orders': chef_orders})
    
    return Analytics(
        totalChefs=total_chefs,
        totalRevenue=total_revenue,
        totalOrders=total_orders,
        totalClients=total_clients,
        ordersByType=orders_by_type,
        revenueByDay=revenue_by_day_list,
        chefOrderDistribution=chef_distribution
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()