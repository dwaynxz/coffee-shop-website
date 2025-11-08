from flask import Flask, render_template, request, redirect, url_for, flash, session
import secrets
from extensions import db, bcrypt, login_manager
from flask_login import login_user, logout_user, current_user,  login_required
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///coffee_shop_db.db"
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "danger"
from models import User, Cart, CartItem, MenuItem, PaymentInfo

def get_unpaid_cart(user_id):
    return Cart.query.filter_by(user_id=user_id, paid=False).first()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

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
    menu_drinks = MenuItem.query.filter_by(category="drinks")
    return render_template("menu.html",  menu_drinks=menu_drinks)

@app.route("/menu-2")
def menu_2():
    menu_breakfast = MenuItem.query.filter_by(category="breakfast")
    return render_template("menu_2.html", menu_breakfast=menu_breakfast)

@app.route("/menu-3")
def menu_3():
    menu_desserts = MenuItem.query.filter_by(category="desserts")
    return render_template("menu_3.html", menu_desserts=menu_desserts)

@app.route("/cart")
@login_required
def cart():
    cart = get_unpaid_cart(user_id=current_user.id)
    if cart:
        cart_items = cart.cart_item
        total = 0
        if cart_items:
            for item in cart_items:
                total += item.menuitem.price
        cart.total = float(total)
        db.session.commit()
        cart_length = len(cart_items)
    return render_template("cart.html", cart=cart,cart_length=cart_length ,cart_items=cart_items)


@app.route("/add-cart", methods=["POST", "GET"])
@login_required
def add_cart():
    item_id = request.form.get("item_id")
    cart = get_unpaid_cart(user_id=current_user.id)
    cart_item = CartItem(cart_id=cart.cart_id, menu_item_id=int(item_id))
    db.session.add(cart_item)
    db.session.commit()
    flash(f"Added {cart_item.menuitem.name} to cart", "success")
    return redirect(url_for("menu"))

@app.route("/remove-item", methods=["POST"])
@login_required
def remove_item():
    item = request.form.get("item")
    cart_item = db.session.get(CartItem, int(item))
    db.session.delete(cart_item)
    flash(f"Removed {cart_item.menuitem.name} from cart", "danger")
    db.session.commit()
    return redirect(url_for("cart"))

@app.route("/payment", methods=["POST"])
@login_required
def payment():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    total = cart.total
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = [i for i in range(2025,2036)]
    return render_template("payment.html", total=total, months=months, years=years)

@app.route("/payment-success", methods=["POST"])
@login_required
def payment_success():
    cost = request.form.get("cost")
    cost = float(cost)
    name = request.form.get("name")
    card_num = request.form.get("card_num")
    security_code = request.form.get("cvv")
    if not name:
        flash("Name field can't be empty", "danger")
        return render_template("payment.html", total=session["total"])
    if not card_num:
        flash("Card number field can't be empty", "danger")
        return render_template("payment.html", name=name, total=session["total"])
    if not security_code:
        flash("Cvv field can't be empty", "danger")
        return render_template("payment.html", name=name, card_num=card_num, total=session["total"])
    if len(card_num) < 16:
        flash("Invalid card number", "danger")
        return render_template("payment.html", name=name, card_num=card_num, cvv=security_code, total=session["total"])
    payment_info = PaymentInfo(name=name, card_num=card_num, cvv=security_code, user_id=current_user.id)
    db.session.add(payment_info)
    db.session.commit()
    current_cart = get_unpaid_cart(user_id=current_user.id)
    current_cart.paid = True
    db.session.commit()
    new_cart = Cart(user_id=current_user.id, paid=False, total=0)
    db.session.add(new_cart)
    db.session.commit()
    return render_template("payment_success.html", cost=cost)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        forename = request.form.get("forename")
        if not forename:
            flash("Forename field can't be empty", "danger")
        else:
            lastname = request.form.get("lastname")
            if not lastname:
                flash("Lastname filed can't be empty", "danger")
                return render_template("register.html", forename=forename)
            else:
                email = request.form.get("email")
                if not email:
                    flash("Email field can't be empty", "danger")
                    return render_template("register.html", forename=forename, lastname=lastname)
                else:
                    password = request.form.get("password")
                    if not password:
                        flash("Password field can't be empty", "danger")
                        return render_template("register.html", forename=forename, lastname=lastname, email=email)
                    else:
                        confirm_password = request.form.get("confirm_password")
                        if not confirm_password:
                            flash("Confirm Password field can't be empty", "danger")
                            return render_template("register.html", forename=forename, lastname=lastname, email=email, password=password)
                        else:
                            if confirm_password != password:
                                flash("Passwords do not match.", "danger")
                                return render_template("register.html", forename=forename, lastname=lastname, email=email, password=password)
                            else:
                                hashed_password = bcrypt.generate_password_hash(password)
                                user = User(forename=forename, lastname=lastname, email=email, password=hashed_password, admin=False)
                                db.session.add(user)
                                db.session.commit()
                                flash("Registered Successfully", "success")
                                return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email:
            flash("Email field can't be empty", "danger")
            return redirect(url_for("login"))
        if not password:
            flash("Password field can't be empty", "danger")
            return render_template("login.html", email=email)
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email doesn't exist. Please register", "danger")
            return render_template("login.html", email=email)
        check_password = bcrypt.check_password_hash(user.password, password)
        if not check_password:
            flash("Incorrect Password", "danger")
            return render_template("login.html", email=email)
        login_user(user)
        check_cart = Cart.query.filter_by(user_id=user.id).filter_by().first()
        if not check_cart:
            cart = Cart(user_id=user.id, paid=False, total=0)
            db.session.add(cart)
            db.session.commit()
        flash("Logged in successfully", "success")
        return redirect(url_for("menu"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("homepage"))

@app.route("/admin/menu")
def admin_menu():
    menu_list = MenuItem.query.all()
    return render_template("admin-menu.html", menu=menu_list)

@app.route("/remove-menu-item", methods=["POST"])
def remove_menu_item():
    menu_id = int(request.form.get("item_id"))
    cart_items = CartItem.query.filter_by(menu_item_id=menu_id)
    for item in cart_items:
        db.session.delete(item)
        db.session.commit()
    menu_item = db.session.get(MenuItem, menu_id)
    db.session.delete(menu_item)
    db.session.commit()
    flash(f"Removed {menu_item.name}", "success")
    return redirect(url_for("admin_menu"))

@app.route("/add-menu-item", methods=["POST"])
def add_menu_item():
    item_name = request.form.get("name")
    price = float(request.form.get("price"))
    image = request.files.get("image")
    category = request.form.get("category")
    if not item_name:
        flash("Item name can't be empty", "error")
        return render_template("admin-menu.html")
    if not price:
        flash("Price field can't be empty", "error")
        return render_template("admin-menu.html",  name=item_name)
    if not image:
        flash("Please add an image", "error")
        return render_template("admin-menu.html", name=item_name, price=price)
    if not category:
        flash("Category field can't be empty", "error")
        return render_template("admin-menu.html", name=item_name, price=price)
    filename = item_name+".png"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(filepath)
    new_menu_item = MenuItem(name=item_name, price=price, image_url=filename, category=category)
    db.session.add(new_menu_item)
    db.session.commit()
    flash(f"Added {item_name} to menu items", "success")
    return redirect(url_for("admin_menu"))

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email:
            flash("Email field can't be empty", "error")
            return render_template("admin-login")
        if not password:
            flash("Password field can't be empty")
            return render_template("admin-login")
        admin = User.query.filter_by(email=email).first()
        if not admin.admin:
            flash("This account is not an admin")
            return redirect(url_for("admin_login"))
        if not bcrypt.check_password_hash(admin.password, password):
            flash("Incorrect password")
            return redirect(url_for("admin_login"))
        if current_user.is_authenticated:
            logout_user()
        login_user(admin)
        return redirect(url_for("admin_menu"))

    return render_template("admin-login.html")

if __name__ == "__main__":
    app.run(debug=True)
