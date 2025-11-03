from extensions import db 
from sqlalchemy import Numeric

class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    forename = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    cart = db.relationship("Cart", backref="user", lazy=True)

class Cart(db.Model):
    __tablename__ = "Carts"
    cart_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    paid = db.Column(db.String, nullable=False)
    cart_item = db.relationship("CartItem", backref="cart", lazy=True)

class CartItem(db.Model):
    __tablename__ = "Cart_Items"
    item_id = db.Column(db.Integer, primary_key=True, nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey("Carts.cart_id"), nullable=False)
    menu_item = db.Column(db.Integer, db.ForeignKey("Menu_Items.item_id"), nullable=False)

class MenuItem(db.Model):
    __tablename__ = "Menu_Items"
    item_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(Numeric(5, 2), nullable=False)
    image_url = db.Column(db.String, nullable=False)
    cart_item = db.relationship("CartItem", backref="menuitem", lazy=True)
    category = db.Column(db.String, nullable=False)

