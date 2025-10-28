
import os
import logging
import random
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")


MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGO_URL")
if not MONGO_URI:
    raise RuntimeError(
        "Missing MongoDB connection string. Set MONGO_URI or MONGO_URL environment variable."
    )

DB_NAME = os.getenv("DB_NAME", "restaurant")


client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database(DB_NAME)


app = FastAPI(title="Restaurant Management API")
api_router = APIRouter(prefix="/api")


cors_origins = os.getenv("CORS_ORIGINS", "*")

if cors_origins.strip() == "*":
    allow_origins = ["*"]
else:
    allow_origins = [u.strip() for u in cors_origins.split(",") if u.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(ROOT_DIR, "static")
if os.path.isdir(static_dir):
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    averagePreparationTime: int
    imageUrl: Optional[str] = None

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    averagePreparationTime: int
    imageUrl: Optional[str] = None

class Table(BaseModel):
    id: str
    number: int
    chairCount: int
    name: Optional[str] = None
    status: str = "available"
    customerId: Optional[str] = None

class TableCreate(BaseModel):
    chairCount: int
    name: Optional[str] = None

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
    type: str
    status: str
    totalAmount: float
    taxes: float
    deliveryCharge: float
    grandTotal: float
    processingTime: int
    remainingTime: int
    createdAt: str
    assignedChef: Optional[str] = None

class OrderCreate(BaseModel):
    tableNumber: Optional[int] = None
    customerName: str
    customerPhone: str
    customerAddress: Optional[str] = None
    items: List[OrderItem]
    type: str
    cookingInstructions: Optional[str] = None

class Customer(BaseModel):
    id: str
    name: str
    phone: str
    address: Optional[str] = None
    ordersCount: int = 0

class Chef(BaseModel):
    id: str
    name: str
    currentOrders: int = 0

class ChefCreate(BaseModel):
    name: str

class Analytics(BaseModel):
    totalChefs: int
    totalRevenue: float
    totalOrders: int
    totalClients: int
    ordersByType: dict
    revenueByDay: List[dict]
    chefOrderDistribution: List[dict]


async def get_next_order_number():
    count = await db.orders.count_documents({})
    return f"{count + 108}"

async def get_next_table_number():
    tables = await db.tables.find({}).to_list(1000)
    if not tables:
        return 1
    numbers = [t['number'] for t in tables]
    return max(numbers) + 1

async def assign_chef_to_order():
    chefs = await db.chefs.find({}).to_list(1000)
    if not chefs:
        return None
    chefs_sorted = sorted(chefs, key=lambda x: x['currentOrders'])
    min_orders = chefs_sorted[0]['currentOrders']
    available_chefs = [c for c in chefs_sorted if c['currentOrders'] == min_orders]
    selected_chef = random.choice(available_chefs)
    await db.chefs.update_one({'id': selected_chef['id']}, {'$inc': {'currentOrders': 1}})
    return selected_chef['name']

async def calculate_order_timing(items):
    total_time = 0
    for item in items:
        menu_item = await db.menu_items.find_one({'id': item['menuItemId']})
        if menu_item:
            total_time += menu_item['averagePreparationTime'] * item['quantity']
    return total_time * 60


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
    result = await db.menu_items.update_one({'id': item_id}, {'$set': item_dict})
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
    categories = await db.menu_items.distinct('category')
    return {"categories": categories}

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
    update_data = {'status': status}
    if customer_id:
        update_data['customerId'] = customer_id
    elif status == 'available':
        update_data['customerId'] = None
    result = await db.tables.update_one({'id': table_id}, {'$set': update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Table not found")
    updated_table = await db.tables.find_one({'id': table_id}, {'_id': 0})
    return Table(**updated_table)

@api_router.delete("/tables/{table_id}")
async def delete_table(table_id: str):
    table = await db.tables.find_one({'id': table_id})
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    if table['status'] == 'reserved':
        raise HTTPException(status_code=400, detail="Cannot delete reserved table")
    table_number = table['number']
    await db.tables.delete_one({'id': table_id})
    tables = await db.tables.find({'number': {'$gt': table_number}}).sort('number', 1).to_list(1000)
    for t in tables:
        await db.tables.update_one({'id': t['id']}, {'$set': {'number': t['number'] - 1}})
    return {"message": "Table deleted and numbers reshuffled"}

@api_router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    if order.type == 'dinein' and order.tableNumber:
        table = await db.tables.find_one({'number': order.tableNumber})
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        if table.get('status') == 'reserved':
            raise HTTPException(status_code=400, detail="Table reserved!!!")
    order_number = await get_next_order_number()
    order_id = f"order_{datetime.now().timestamp()}"
    item_total = sum(item.price * item.quantity for item in order.items)
    taxes = item_total * 0.05
    delivery_charge = 50 if order.type == 'takeaway' else 0
    grand_total = item_total + taxes + delivery_charge
    processing_time = await calculate_order_timing([item.model_dump() for item in order.items])
    assigned_chef = await assign_chef_to_order()
    if order.type == 'dinein' and order.tableNumber:
        await db.tables.update_one({'number': order.tableNumber}, {'$set': {'status': 'reserved'}})
    customer = await db.customers.find_one({'phone': order.customerPhone})
    if customer:
        await db.customers.update_one({'phone': order.customerPhone}, {'$inc': {'ordersCount': 1}})
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
    order_dict.update({
        'id': order_id,
        'orderNumber': order_number,
        'status': 'processing',
        'totalAmount': item_total,
        'taxes': taxes,
        'deliveryCharge': delivery_charge,
        'grandTotal': grand_total,
        'processingTime': processing_time,
        'remainingTime': processing_time,
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'assignedChef': assigned_chef
    })
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
    for order in orders:
        if order['status'] == 'processing':
            created_at = datetime.fromisoformat(order['createdAt'])
            elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
            remaining = max(0, order['processingTime'] - int(elapsed))
            order['remainingTime'] = remaining
            if remaining == 0:
                await db.orders.update_one({'id': order['id']}, {'$set': {'status': 'done', 'remainingTime': 0}})
                order['status'] = 'done'
                if order.get('type') == 'dinein' and order.get('tableNumber'):
                    await db.tables.update_one({'number': order['tableNumber']}, {'$set': {'status': 'available'}})
        else:
            order['remainingTime'] = 0
    return orders

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order['status'] == 'processing':
        created_at = datetime.fromisoformat(order['createdAt'])
        elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
        remaining = max(0, order['processingTime'] - int(elapsed))
        order['remainingTime'] = remaining
        if remaining == 0:
            await db.orders.update_one({'id': order_id}, {'$set': {'status': 'done', 'remainingTime': 0}})
            order['status'] = 'done'
            if order.get('type') == 'dinein' and order.get('tableNumber'):
                await db.tables.update_one({'number': order['tableNumber']}, {'$set': {'status': 'available'}})
    return order

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    order = await db.orders.find_one({'id': order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    result = await db.orders.update_one({'id': order_id}, {'$set': {'status': status}})
    if status == 'done' and order['type'] == 'dinein' and order.get('tableNumber'):
        await db.tables.update_one({'number': order['tableNumber']}, {'$set': {'status': 'available'}})
    if status == 'completed':
        if order.get('assignedChef'):
            await db.chefs.update_one({'name': order['assignedChef']}, {'$inc': {'currentOrders': -1}})
    updated_order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    return Order(**updated_order)

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
    result = await db.chefs.update_one({'id': chef_id}, {'$set': chef_dict})
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

@api_router.get("/analytics", response_model=Analytics)
async def get_analytics():
    total_chefs = await db.chefs.count_documents({})
    orders = await db.orders.find({}, {'_id': 0}).to_list(10000)
    total_revenue = sum(order['grandTotal'] for order in orders)
    total_orders = len(orders)
    total_clients = await db.customers.count_documents({})
    dinein_orders = len([o for o in orders if o['type'] == 'dinein'])
    takeaway_orders = len([o for o in orders if o['type'] == 'takeaway'])
    served_orders = len([o for o in orders if o['status'] == 'done' or o['status'] == 'completed'])
    orders_by_type = {'dinein': dinein_orders, 'takeaway': takeaway_orders, 'served': served_orders}
    revenue_by_day = {}
    for order in orders:
        created_at = datetime.fromisoformat(order['createdAt'])
        day = created_at.strftime('%a')
        if day not in revenue_by_day:
            revenue_by_day[day] = 0
        revenue_by_day[day] += order['grandTotal']
    revenue_by_day_list = [{'day': day, 'revenue': revenue} for day, revenue in revenue_by_day.items()]
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


app.include_router(api_router)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "API is running. Visit /docs for API docs."}
