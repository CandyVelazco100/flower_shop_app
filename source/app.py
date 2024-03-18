# ----- Imports -----

# Flask Imports
from flask_mysqldb import MySQL
from flask_login import *
from flask import *
# Flask Imports

# Python Imports
from functools import wraps
from config import config
# Python Imports

# Models Imports
from models.model_users import ModelUsers
from models.model_orders import ModelOrders
from models.model_products import ModelProducts
from models.model_shopping_cart import ModelShoppingCart
# Models Imports

# Entities Imports
from models.entities.users import Users
from models.entities.orders import Orders
from models.entities.products import Products
from models.entities.shopping_cart import ShoppingCart
# Entities Imports

# ----- Imports -----





# ----- App Configuration -----

# Flask Configuration
app = Flask(__name__)
db = MySQL(app)
# Flask Configuration

# Login Configuration
login_manager_app = LoginManager(app)
# Login Configuration

# ----- App Configuration -----





# ----- Authentication -----

# Root Route
@app.route("/")

def index():

    return redirect("login")
# Root Route

# Login Route
@app.route("/login", methods=["GET", "POST"])

def login():
    if current_user.is_authenticated == False:
        if request.method == "POST":
            user = Users (
                0,
                request.form["usernameInput"],
                request.form["passwordInput"],
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                ""
            )
            
            logged_user = ModelUsers.login(db, user)

            if logged_user is not None:
                if logged_user.user_type == 1 or logged_user.user_type == 2 or logged_user.user_type == 0:  
                    login_user(logged_user)
                    return redirect(url_for("dashboard"))
            else:
                flash("Usuario o contraseña incorrectos.")
                return render_template("auth/login.html")
        else:
            return render_template("auth/login.html")
    else:
        return redirect(url_for("dashboard"))
# Login Route

# Sign Up Route
@app.route("/signup", methods=["GET", "POST"])

def signup():

    if request.method == "POST":
        confirm_password = request.form["confirmPasswordInput"]
        user = Users (
            0,
            request.form["usernameInput"],
            request.form["passwordInput"],
            request.form["firstnameInput"],
            request.form["lastnameInput"],
            request.form["emailInput"],
            request.form["addressInput"],
            request.form["phoneInput"],
            "None",
            "None",
            0
        )

        try:
            if user.password != confirm_password:
                flash("Las contraseñas no coinciden.")
                return render_template("auth/signup.html")
            else:
                ModelUsers.add_user(db, user)
                
                flash("Usuario registrado correctamente.")
                return redirect(url_for("login"))
        except Exception as e:
            flash("Error al registrar usuario. %s" % e)
    else:
        return render_template("auth/signup.html")
# Sign Up Route

# Error 401 Route
@app.route("/error-401")

def error_401():
    
    return render_template("auth/error-401.html")
# Error 401 Route

# Error 403 Route
@app.route("/error-403")

def error_403():
    
    return render_template("auth/error-403.html")
# Error 403 Route

# Login Required Decorator
def login_is_required(func):
    
    @wraps(func)
    
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("error_401"))
        else:
            return func(*args, **kwargs)
    
    return decorated_view
# Login Required Decorator

# Admin Required Decorator
def admin_required(func):

    @wraps(func)
    
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 1:
            return redirect(url_for("error_403"))
        else:
            return func(*args, **kwargs)
    
    return decorated_view
# Admin Required Decorator

# Employee Required Decorator
def employee_required(func):

    @wraps(func)
    
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 2:
            return redirect(url_for("error_403"))
        else:
            return func(*args, **kwargs)
    
    return decorated_view
# Employee Required Decorator

# Permission Tagger Decorator
def permission_tagger(func):

    @wraps(func)
    
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated or current_user.user_type > 0:
            return func(*args, **kwargs)
        else:
            return redirect(url_for("error_403"))
            
    
    return decorated_view
# Permission Tagger Decorator

# Logout Route
@app.route("/logout")
@login_is_required

def logout():

    logout_user()
    return redirect(url_for("login"))
# Logout Route

# User Loader
@login_manager_app.user_loader

def load_user(id):

    return ModelUsers.get_users_by_id(db, id)
# User Loader

# ----- Authentication -----





# ----- Dashboard -----

# Get Count Shopping Cart Function
def get_count_shopping_cart(user_id):
    
    return ModelShoppingCart.get_count_shopping_cart(db, user_id)
# Get Count Shopping Cart Function

# Get Count Notifications Function
def get_count_notifications():
    
    return len(ModelProducts.reorder_product_alert(db))
# Get Count Notifications Function

# Get Notifications Function
def get_notifications():
        
        return ModelProducts.reorder_product_alert(db)
# Get Notifications Function

# Dashboard Route
@app.route("/dashboard")
@login_is_required

def dashboard():
    
    return render_template (
        "public/dashboard.html",
        get_count_shopping_cart=get_count_shopping_cart(current_user.id),
        get_count_notifications=get_count_notifications()
    )
# Dashboard Route

# ----- Dashboard -----





# ----- Notifications -----
@app.route("/notifications")
@login_is_required
@permission_tagger

def notifications():
        return render_template (
            "public/notifications.html",
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(),
            notifications=get_notifications()
        )
# ----- Notifications -----





# ----- Products -----

# Validate Form Function
def validate_form(product) -> bool:
    if len(product.name) == 0:
        flash("Nombre no puede estar vacío.")
    if len(product.description) == 0:
        flash("Descripción no puede estar vacío.")
    if len(product.price) == 0:
        flash("Precio no puede estar vacío.")
    if float(product.price) < 0:
        flash("Precio no puede ser negativo.")
    return True
# Validate Form Function

# Products Route
@app.route("/products")
@login_is_required
@admin_required

def products():

    try:
        products = ModelProducts.get_products(db)
        
        return render_template (
            "public/products-add.html", 
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(),
            products=products
        )
    except Exception as e:
        raise Exception(e)
# Products Route

# Products Read Only Route
@app.route("/products-readonly")
@login_is_required
@employee_required

def productsReadOnly():

    try:
        products = ModelProducts.get_products(db)
        
        return render_template (
            "public/products-employee.html", 
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(),
            products=products
        )
    except Exception as e:
        raise Exception(e)
# Products Read Only Route

# Add Product Route
@app.route("/products/add", methods=["GET", "POST"])
@login_is_required
@admin_required

def add_product():

    if request.method == "POST":
        product = Products (
            0,
            request.form["nameInput"],
            request.form["descriptionInput"],
            request.form["quantityInput"],
            request.form["alertQuantityInput"],
            request.form["priceInput"],
            request.form["imageInput"]
        )

        if validate_form(product):      
            try:
                ModelProducts.add_product(db, product)

                flash("Producto agregado correctamente.")
                return redirect(url_for("products"))
            except Exception as e:
                flash("Error al actualizar producto. %s" % e)
        else:
            return render_template (
                "public/products-add.html",
                get_count_shopping_cart=get_count_shopping_cart(current_user.id),
                get_count_notifications=get_count_notifications()
            )
    return redirect(url_for("products"))
# Add Product Route

# Edit Product Route
@app.route("/products/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required

def edit_product(id):

    if request.method == "POST":
        product = Products (
        id,
        request.form["nameInput"],
        request.form["descriptionInput"],
        request.form["quantityInput"],
        request.form["alertQuantityInput"],
        request.form["priceInput"],
        request.form["imageInput"]
        )
        
        if validate_form(product):
            try:
                ModelProducts.edit_product(db, product)

                flash("Producto actualizado correctamente.")
                return redirect(url_for("products"))
            except Exception as e:
                flash("Error al actualizar producto. %s" % e)
        
        return redirect(url_for("products"))
    else:
        return render_template (
            "public/products-edit.html", 
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(), 
            product=ModelProducts.get_products_by_id(db, id),
            id=id
        )
# Edit Product Route

# Delete Product Route
@app.route("/products/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required

def delete_product(id):

    if request.method == "POST":
        ModelProducts.delete_product(db, id)

        flash("Producto eliminado correctamente.")
        return redirect(url_for("products"))
    else:
        return render_template (
            "public/products-delete.html",
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(),
            id=id
        )
# Delete Product Route

# ----- Products -----
    




# ----- Users -----

# Users Route
@app.route("/users")
@login_is_required
@admin_required

def users():
    
    try:
        users = ModelUsers.get_users(db)

        return render_template (
            "public/users-add.html",
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(),
            users=users
        )
    except Exception as e:
        raise Exception(e)
# Users Route

# Users Read Only Route
@app.route("/users-readonly")
@login_is_required
@employee_required

def usersReadOnly():
    
    try:
        users = ModelUsers.get_users(db)

        return render_template (
            "public/users-employee.html",
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(),
            users=users
        )
    except Exception as e:
        raise Exception(e)
# Users Read Only Route

# Add User Route
@app.route("/users/add", methods=["GET", "POST"])
@login_is_required
@admin_required

def add_user():

    if request.method == "POST":
        user_type = int()
        if (request.form["userTypeInput"] == "Cliente"):
            user_type = 0
        elif (request.form["userTypeInput"] == "Administrador"):
            user_type = 1
        elif (request.form["userTypeInput"] == "Empleado"):
            user_type = 2

        user = Users (
            0,
            request.form["usernameInput"],
            request.form["passwordInput"],
            request.form["firstnameInput"],
            request.form["lastnameInput"],
            request.form["emailInput"],
            request.form["addressInput"],
            request.form["phoneInput"],
            request.form["startTimeInput"],
            request.form["endTimeInput"],
            user_type
        )

        try:
            ModelUsers.add_user(db, user)

            flash("Usuario agregado correctamente.")
            return redirect(url_for("users"))
        except Exception as e:
            flash("Error al agregar usuario. %s" % e)
    else:
        return render_template (
            "public/users-add.html",
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications()
        )
# Add User Route

# Edit User Route
@app.route("/users/edit/<int:id>", methods=["GET", "POST"])
@login_is_required
@admin_required

def edit_user(id):
    
    if request.method == "POST":
        user_type = int()
        if (request.form["userTypeInput"] == "Cliente"):
            user_type = 0
        elif (request.form["userTypeInput"] == "Administrador"):
            user_type = 1
        elif (request.form["userTypeInput"] == "Empleado"):
            user_type = 2

        user = Users (
            id,
            request.form["usernameInput"],
            request.form["passwordInput"],
            request.form["firstnameInput"],
            request.form["lastnameInput"],
            request.form["emailInput"],
            request.form["addressInput"],
            request.form["phoneInput"],
            request.form["startTimeInput"],
            request.form["endTimeInput"],
            user_type
        )

        try:
            ModelUsers.edit_user(db, user)

            flash("Usuario actualizado correctamente.")
            return redirect(url_for("users"))
        except Exception as e:
            flash("Error al actualizar usuario. %s" % e)
    else:
        return render_template (
            "public/users-edit.html",
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            user=ModelUsers.get_users_by_id(db, id),
            get_count_notifications=get_count_notifications(),
            id=id
        )
# Edit User Route

# Delete User Route
@app.route("/users/delete/<int:id>", methods=["GET", "POST"])
@login_is_required
@admin_required

def delete_user(id):

    if request.method == "POST":
        ModelUsers.delete_user(db, id)

        flash("Usuario eliminado correctamente.")
        return redirect(url_for("users"))
    else:
        return render_template (
            "public/users-delete.html",
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_count_notifications=get_count_notifications(),
            id=id
        )
# Delete User Route

# ----- Users -----
    




# ----- Shop -----

# Is Empty Shopping Cart Function
def is_empty_shopping_cart(user_id):
    
    if ModelShoppingCart.get_count_shopping_cart(db, user_id) == 0:
        return True
    else:
        return False
# Is Empty Shopping Cart Function

# Shop Route
@app.route("/shop")
@login_required

def shop():
    
    try:
        products = ModelProducts.get_products(db)
        shopping_cart_products = ModelShoppingCart.get_essential_data(db, current_user.id)

        return render_template (
            "public/shop.html", 
            get_count_shopping_cart=get_count_shopping_cart(current_user.id),
            get_total_price=ModelShoppingCart.get_total_price(db, current_user.id),
            is_empty_shopping_cart=is_empty_shopping_cart(current_user.id),
            products=products, 
            shopping_cart_products=shopping_cart_products
        )
    except Exception as e:
        raise Exception(e)
# Shop Route

# Add to Shopping Cart Route
@app.route("/shop/add/<int:id>", methods=["GET", "POST"])
@login_required

def add_shopping_cart(id):
    
    if request.method == "POST":
        shopping_cart = ShoppingCart (
            0,
            current_user.id,
            id,
            request.form["quantityInput_%s" % id]
        )

        ModelShoppingCart.add_shopping_cart(db, shopping_cart)

        flash("Producto agregado al carrito de compras correctamente.")
        return redirect(url_for("shop"))
    else:
        return redirect(url_for("shop"))
# Add to Shopping Cart Route

# Remove from Shopping Cart Route
@app.route("/shop/remove/<int:id>", methods=["GET", "POST"])
@login_required

def remove_from_shopping_cart(id):

    if request.method == "POST":
        ModelShoppingCart.remove_from_shopping_cart(db, current_user.id, id)
        
        flash("Producto eliminado del carrito de compras correctamente.")
        return redirect(url_for("shop"))
    else:
        return redirect(url_for("shop"))
# Remove from Shopping Cart Route

# Clear Shopping Cart Route
@app.route("/shop/clear")
@login_required

def clear_shopping_cart():
    
    ModelShoppingCart.clear_shopping_cart(db, current_user.id)
    
    flash("Carrito de compras vaciado correctamente.")
    return redirect(url_for("shop"))
# Clear Shopping Cart Route

# ----- Shop -----





# ----- Receipt -----

# is Empty Receipt Function
def is_empty_receipt():
    
    if ModelOrders.get_count_orders_by_user(db, current_user.id) == 0:
        return True
    else:
        return False
# is Empty Receipt Function

# Receipt Route
@app.route("/shop/receipt", methods=["GET", "POST"])
@login_required

def receipt():

    if request.method == "POST":
        if is_empty_shopping_cart(current_user.id):
            flash("No se puede generar una orden vacía.")
            return redirect(url_for("shop"))
        else:
            try:
                shopping_cart = ModelShoppingCart.get_shopping_cart(db, current_user.id)
                essential_data = ModelShoppingCart.get_essential_data(db, current_user.id)
                get_users_by_id = ModelUsers.get_users_by_id(db, current_user.id)
                get_total_price = ModelShoppingCart.get_total_price(db, current_user.id)
                get_last_order_id = ModelOrders.get_last_order_id(db)
                
                for product in shopping_cart:
                    order = Orders (
                        get_last_order_id,
                        current_user.id,
                        product[2],
                        product[3]
                    )
                    
                    ModelProducts.buy_product(db, product[2], product[3])

                ModelOrders.add_order(db, order)
                
                ModelShoppingCart.clear_shopping_cart(db, current_user.id)
                get_orders_by_id = ModelOrders.get_orders_by_id(db, get_last_order_id)
                
                return render_template (
                    "public/receipt.html",
                    shopping_cart=essential_data,
                    total_price=get_total_price,
                    user_information=get_users_by_id,
                    order_information=get_orders_by_id
                )
            except Exception as e:
                raise Exception(e)
    else:
        return redirect(url_for("shop"))
# Receipt Route
    
# ----- Receipt -----
    




# ----- Main -----

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()

# ----- Main -----