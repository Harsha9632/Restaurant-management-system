import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def seed_database():
    print("Starting database seeding...")
    
    
    await db.menu_items.delete_many({})
    await db.tables.delete_many({})
    await db.orders.delete_many({})
    await db.customers.delete_many({})
    await db.chefs.delete_many({})
    print("Cleared existing data")
    
    
    chefs = [
        {"id": "chef_1", "name": "Harshavardhan", "currentOrders": 0},
        {"id": "chef_2", "name": "Jalsa", "currentOrders": 0},
        {"id": "chef_3", "name": "Anjan", "currentOrders": 0},
        {"id": "chef_4", "name": "Madhu", "currentOrders": 0}
    ]
    await db.chefs.insert_many(chefs)
    print(f" Created {len(chefs)} chefs")
    
    
    menu_items = [
        
        {"id": "menu_burger_1", "name": "Classic Burger", "description": "Juicy beef patty with lettuce, tomato, and special sauce", "price": 250, "category": "Burger", "stock": 50, "averagePreparationTime": 10, "imageUrl": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400"},
        {"id": "menu_burger_2", "name": "Cheese Burger", "description": "Classic burger with melted cheese", "price": 280, "category": "Burger", "stock": 50, "averagePreparationTime": 10, "imageUrl": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=400"},
        {"id": "menu_burger_3", "name": "Double Cheeseburger", "description": "Two beef patties with double cheese", "price": 350, "category": "Burger", "stock": 40, "averagePreparationTime": 12, "imageUrl": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=400"},
        {"id": "menu_burger_4", "name": "Veggie Burger", "description": "Delicious vegetarian patty with fresh veggies", "price": 220, "category": "Burger", "stock": 30, "averagePreparationTime": 8, "imageUrl": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?w=400"},
        {"id": "menu_burger_5", "name": "Bacon Burger", "description": "Beef patty with crispy bacon strips", "price": 320, "category": "Burger", "stock": 35, "averagePreparationTime": 11, "imageUrl": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400"},
        {"id": "menu_burger_6", "name": "Chicken Burger", "description": "Grilled chicken breast with mayo", "price": 260, "category": "Burger", "stock": 45, "averagePreparationTime": 10, "imageUrl": "https://images.unsplash.com/photo-1562547682-6f9a2c3e3aba?w=400"},
        {"id": "menu_burger_7", "name": "Mushroom Swiss Burger", "description": "Beef patty with sautéed mushrooms and Swiss cheese", "price": 300, "category": "Burger", "stock": 30, "averagePreparationTime": 12, "imageUrl": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=400"},
        {"id": "menu_burger_8", "name": "Spicy Jalapeño Burger", "description": "Spicy burger with jalapeños and pepper jack cheese", "price": 290, "category": "Burger", "stock": 35, "averagePreparationTime": 11, "imageUrl": "https://images.unsplash.com/photo-1521305916504-4a1121188589?w=400"},
        
        
        {"id": "menu_pizza_1", "name": "Marinara", "description": "Traditional tomato sauce with garlic and oregano", "price": 300, "category": "Pizza", "stock": 30, "averagePreparationTime": 15, "imageUrl": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400"},
        {"id": "menu_pizza_2", "name": "Pepperoni", "description": "Classic pepperoni with mozzarella cheese", "price": 350, "category": "Pizza", "stock": 40, "averagePreparationTime": 15, "imageUrl": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400"},
        {"id": "menu_pizza_3", "name": "Sicilian", "description": "Thick crust pizza with rich tomato sauce", "price": 340, "category": "Pizza", "stock": 25, "averagePreparationTime": 18, "imageUrl": "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?w=400"},
        {"id": "menu_pizza_4", "name": "Capricciosa", "description": "Ham, mushrooms, artichokes, and olives", "price": 380, "category": "Pizza", "stock": 30, "averagePreparationTime": 16, "imageUrl": "https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=400"},
        {"id": "menu_pizza_5", "name": "Margherita", "description": "Fresh mozzarella, tomatoes, and basil", "price": 290, "category": "Pizza", "stock": 35, "averagePreparationTime": 14, "imageUrl": "https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400"},
        {"id": "menu_pizza_6", "name": "Veggie Supreme", "description": "Loaded with fresh vegetables", "price": 330, "category": "Pizza", "stock": 28, "averagePreparationTime": 16, "imageUrl": "https://images.unsplash.com/photo-1511688878353-3a2f5be94cd7?w=400"},
        {"id": "menu_pizza_7", "name": "BBQ Chicken", "description": "BBQ sauce, grilled chicken, and red onions", "price": 360, "category": "Pizza", "stock": 32, "averagePreparationTime": 17, "imageUrl": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400"},
        {"id": "menu_pizza_8", "name": "Hawaiian", "description": "Ham, pineapple, and mozzarella", "price": 340, "category": "Pizza", "stock": 30, "averagePreparationTime": 15, "imageUrl": "https://images.unsplash.com/photo-1576458088443-04a19c4a1c39?w=400"},
        
        
        {"id": "menu_drink_1", "name": "Coca-Cola", "description": "Classic Coca-Cola", "price": 60, "category": "Drink", "stock": 100, "averagePreparationTime": 1, "imageUrl": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400"},
        {"id": "menu_drink_2", "name": "Fresh Orange Juice", "description": "Freshly squeezed orange juice", "price": 80, "category": "Drink", "stock": 50, "averagePreparationTime": 3, "imageUrl": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400"},
        {"id": "menu_drink_3", "name": "Lemonade", "description": "Refreshing homemade lemonade", "price": 70, "category": "Drink", "stock": 50, "averagePreparationTime": 2, "imageUrl": "https://images.unsplash.com/photo-1523677011781-c91d1bbe2f9f?w=400"},
        {"id": "menu_drink_4", "name": "Iced Tea", "description": "Cool iced tea with lemon", "price": 65, "category": "Drink", "stock": 60, "averagePreparationTime": 2, "imageUrl": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400"},
        {"id": "menu_drink_5", "name": "Mango Smoothie", "description": "Creamy mango smoothie", "price": 90, "category": "Drink", "stock": 45, "averagePreparationTime": 4, "imageUrl": "https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=400"},
        {"id": "menu_drink_6", "name": "Coffee", "description": "Hot brewed coffee", "price": 50, "category": "Drink", "stock": 80, "averagePreparationTime": 3, "imageUrl": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400"},
        {"id": "menu_drink_7", "name": "Strawberry Milkshake", "description": "Thick strawberry milkshake", "price": 100, "category": "Drink", "stock": 40, "averagePreparationTime": 4, "imageUrl": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400"},
        {"id": "menu_drink_8", "name": "Green Tea", "description": "Hot green tea", "price": 55, "category": "Drink", "stock": 70, "averagePreparationTime": 2, "imageUrl": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400"},
        
        
        {"id": "menu_fries_1", "name": "Classic French Fries", "description": "Crispy golden fries", "price": 120, "category": "French Fries", "stock": 60, "averagePreparationTime": 6, "imageUrl": "https://images.unsplash.com/photo-1585108727903-f9a5c5f1f39d?w=400"},
        {"id": "menu_fries_2", "name": "Cheese Fries", "description": "Fries topped with melted cheese", "price": 150, "category": "French Fries", "stock": 50, "averagePreparationTime": 7, "imageUrl": "https://images.unsplash.com/photo-1630384060421-cb20d0e0649d?w=400"},
        {"id": "menu_fries_3", "name": "Loaded Fries", "description": "Fries with cheese, bacon, and sour cream", "price": 180, "category": "French Fries", "stock": 40, "averagePreparationTime": 8, "imageUrl": "https://images.unsplash.com/photo-1639024471283-03518883512d?w=400"},
        {"id": "menu_fries_4", "name": "Peri-Peri Fries", "description": "Spicy peri-peri seasoned fries", "price": 140, "category": "French Fries", "stock": 45, "averagePreparationTime": 7, "imageUrl": "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?w=400"},
        {"id": "menu_fries_5", "name": "Garlic Parmesan Fries", "description": "Fries with garlic and parmesan", "price": 160, "category": "French Fries", "stock": 40, "averagePreparationTime": 8, "imageUrl": "https://images.unsplash.com/photo-1631452180533-e917d8a4883c?w=400"},
        {"id": "menu_fries_6", "name": "Sweet Potato Fries", "description": "Crispy sweet potato fries", "price": 140, "category": "French Fries", "stock": 35, "averagePreparationTime": 7, "imageUrl": "https://images.unsplash.com/photo-1639744091801-1b1c63efea76?w=400"},
        {"id": "menu_fries_7", "name": "Chili Cheese Fries", "description": "Fries with chili and cheese sauce", "price": 170, "category": "French Fries", "stock": 38, "averagePreparationTime": 9, "imageUrl": "https://images.unsplash.com/photo-1639744091672-e14b30d6c639?w=400"},
        {"id": "menu_fries_8", "name": "Truffle Fries", "description": "Fries with truffle oil and herbs", "price": 190, "category": "French Fries", "stock": 30, "averagePreparationTime": 8, "imageUrl": "https://images.unsplash.com/photo-1623206726588-6eb7ae12c2fd?w=400"},
        
        
        {"id": "menu_veggie_1", "name": "Garden Salad", "description": "Fresh mixed greens with vegetables", "price": 150, "category": "Veggies", "stock": 40, "averagePreparationTime": 5, "imageUrl": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400"},
        {"id": "menu_veggie_2", "name": "Caesar Salad", "description": "Romaine lettuce with Caesar dressing", "price": 180, "category": "Veggies", "stock": 35, "averagePreparationTime": 6, "imageUrl": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400"},
        {"id": "menu_veggie_3", "name": "Grilled Vegetables", "description": "Assorted grilled vegetables", "price": 200, "category": "Veggies", "stock": 30, "averagePreparationTime": 10, "imageUrl": "https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?w=400"},
        {"id": "menu_veggie_4", "name": "Greek Salad", "description": "Feta cheese, olives, and cucumber", "price": 190, "category": "Veggies", "stock": 32, "averagePreparationTime": 6, "imageUrl": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400"},
        {"id": "menu_veggie_5", "name": "Caprese Salad", "description": "Fresh mozzarella, tomato, and basil", "price": 170, "category": "Veggies", "stock": 30, "averagePreparationTime": 5, "imageUrl": "https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=400"},
        {"id": "menu_veggie_6", "name": "Coleslaw", "description": "Creamy cabbage coleslaw", "price": 100, "category": "Veggies", "stock": 50, "averagePreparationTime": 4, "imageUrl": "https://images.unsplash.com/photo-1625938145312-559161d43cfe?w=400"},
        {"id": "menu_veggie_7", "name": "Corn on the Cob", "description": "Grilled corn with butter", "price": 80, "category": "Veggies", "stock": 45, "averagePreparationTime": 8, "imageUrl": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=400"},
        {"id": "menu_veggie_8", "name": "Stuffed Bell Peppers", "description": "Bell peppers stuffed with vegetables", "price": 210, "category": "Veggies", "stock": 25, "averagePreparationTime": 15, "imageUrl": "https://images.unsplash.com/photo-1601001435674-5f6e91bb4c4c?w=400"},
        {"id": "menu_veggie_9", "name": "Vegetable Spring Rolls", "description": "Crispy spring rolls with veggies", "price": 140, "category": "Veggies", "stock": 35, "averagePreparationTime": 8, "imageUrl": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=400"},
        {"id": "menu_veggie_10", "name": "Mushroom Sauté", "description": "Sautéed mushrooms with garlic", "price": 160, "category": "Veggies", "stock": 30, "averagePreparationTime": 7, "imageUrl": "https://images.unsplash.com/photo-1589621316382-008455b857cd?w=400"},
        
        
        {"id": "menu_dessert_1", "name": "Apple Pie", "description": "Classic apple pie with cinnamon", "price": 150, "category": "Dessert", "stock": 25, "averagePreparationTime": 5, "imageUrl": "https://images.unsplash.com/photo-1535920527002-b35e96722eb9?w=400"},
        {"id": "menu_dessert_2", "name": "Ice Cream", "description": "Vanilla ice cream with chocolate sauce", "price": 120, "category": "Dessert", "stock": 40, "averagePreparationTime": 3, "imageUrl": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400"},
        {"id": "menu_dessert_3", "name": "Chocolate Brownie", "description": "Warm chocolate brownie with nuts", "price": 140, "category": "Dessert", "stock": 30, "averagePreparationTime": 6, "imageUrl": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400"},
        {"id": "menu_dessert_4", "name": "Cheesecake", "description": "New York style cheesecake", "price": 160, "category": "Dessert", "stock": 20, "averagePreparationTime": 4, "imageUrl": "https://images.unsplash.com/photo-1533134242820-3a7e73d7b0ba?w=400"},
        {"id": "menu_dessert_5", "name": "Tiramisu", "description": "Italian coffee-flavored dessert", "price": 170, "category": "Dessert", "stock": 18, "averagePreparationTime": 5, "imageUrl": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400"},
        {"id": "menu_dessert_6", "name": "Donut", "description": "Glazed donut with sprinkles", "price": 80, "category": "Dessert", "stock": 50, "averagePreparationTime": 2, "imageUrl": "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400"},
        {"id": "menu_dessert_7", "name": "Chocolate Lava Cake", "description": "Molten chocolate center", "price": 180, "category": "Dessert", "stock": 22, "averagePreparationTime": 8, "imageUrl": "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400"},
        {"id": "menu_dessert_8", "name": "Panna Cotta", "description": "Italian cream dessert", "price": 150, "category": "Dessert", "stock": 25, "averagePreparationTime": 5, "imageUrl": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400"},
    ]
    await db.menu_items.insert_many(menu_items)
    print(f"Created {len(menu_items)} menu items")
    
    
    tables = []
    for i in range(1, 31):
        chair_count = [2, 4, 6, 8][i % 4]
        tables.append({
            "id": f"table_{i}",
            "number": i,
            "chairCount": chair_count,
            "name": f"Table {i}",
            "status": "available",
            "customerId": None
        })
    await db.tables.insert_many(tables)
    print(f" Created {len(tables)} tables")
    
    print("Database seeding completed successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
