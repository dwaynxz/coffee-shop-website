from main import app, db
from models import MenuItem
from menu import drinks, desserts, breakfast
with app.app_context():
    db.create_all()
    print("Database tables created")

    for item, value in drinks.items():
            name = value["name"]
            price = value["price"]
            image_url = item+".png"
            category = "drinks"
            menu_item = MenuItem(name=name, price=price, image_url=image_url, category=category)
            db.session.add(menu_item)
            db.session.commit()
    print("Added drinks to database")
        
    for item,value in desserts.items():
        name = value["name"]
        price = value["price"]
        image_url = item+".png"
        category = "desserts"
        menu_item = MenuItem(name=name, price=price, image_url=image_url, category=category)
        db.session.add(menu_item)
        db.session.commit()
    print("Added desserts to database")
        
    for item, value in breakfast.items():
        name = value["name"]
        price = value["price"]
        image_url = item+".png"
        category = "breakfast"
        menu_item = MenuItem(name=name, price=price, image_url=image_url, category=category)
        db.session.add(menu_item)
        db.session.commit()
    print("Added breakfast itemes to database")
            
print("Done!!!")