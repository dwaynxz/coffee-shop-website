from sqlalchemy.orm import backref

from main import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    forename = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    cart = db.relationship("cart", backref="cart", lazy=True)
