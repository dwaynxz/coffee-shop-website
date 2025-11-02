from sqlalchemy.orm import backref

from main import db

class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    forename = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    cart = db.relationship("cart", backref="user", lazy=True)

class Cart(db.Model):
    __tablename__ = "Carts"
    cart_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.Foreignkey("user.id"), nullable=False)
    paid = db.Column(db.String, nullable=False)
    cart_item = db.relationship("CartItem", backref="cart", lazy=True)


