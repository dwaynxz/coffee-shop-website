from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from menu import drinks, breakfast, desserts
import secrets
from extensions import db


app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///coffee_shop_db.db"
db.init_app(app)
from models import User, Cart, CartItem, MenuItem

my_cart = []

def sum_cart(user_cart):
    total = 0
    for item in user_cart:
        total += item["price"]
    return total

@app.route("/")
@app.route("/home")
def homepage():
    return render_template("homepage.html")
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/menu")
def menu():
    return render_template("menu.html", drinks=drinks)

@app.route("/menu-2")
def menu_2():
    return render_template("menu_2.html", breakfast=breakfast)

@app.route("/menu-3")
def menu_3():
    return render_template("menu_3.html", desserts=desserts)

@app.route("/cart")
def cart():
    length_cart = len(my_cart)
    total = sum_cart(my_cart)
    return render_template("cart.html", my_cart=my_cart, length_cart=length_cart, total=total)

@app.route("/add-cart", methods=["POST", "GET"])
def add_cart():
    item = request.form.get("item")
    price = request.form.get("price")
    my_cart.append({"item": item,
                 "price": float(price)})
    return redirect(url_for("menu"))

@app.route("/remove-item", methods=["POST"])
def remove_item():
    item = request.form.get("item")
    for  i, menu_item in enumerate(my_cart):
        if menu_item["item"] == item:
            my_cart.pop(i)
            break
    return redirect(url_for("cart"))

@app.route("/payment", methods=["POST"])
def payment():
    total = request.form.get("total")
    total = float(total)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = [i for i in range(2025,2036)]
    return render_template("payment.html", total=total, months=months, years=years)

@app.route("/payment-success", methods=["POST"])
def payment_success():
    cost = request.form.get("cost")
    cost = float(cost)
    my_cart.clear()
    return render_template("payment_success.html", cost=cost)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)