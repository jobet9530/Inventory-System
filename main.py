from flask import Flask, request, render_template, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import bleach
import bcrypt
from flask_login import login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
db = SQLAlchemy(app)


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    barcode = db.Column(db.Text, unique=True)
    category = db.Column(db.Text)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Product {self.product_name}>'


class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text)
    phone_number = db.Column(db.Text)
    address = db.Column(db.Text)

    def __repr__(self):
        return f'<Customer {self.customer_name}>'


class Sale(db.Model):
    sale_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    sale_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.Text)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    customer = db.relationship('Customer', backref='sales')
    user = db.relationship('User', backref='sales')

    def __repr__(self):
        return f'<Sale {self.sale_id}>'


class SaleItem(db.Model):
    sale_item_id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.sale_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    item_amount = db.Column(db.Float, nullable=False)
    sale = db.relationship('Sale', backref='items')
    product = db.relationship('Product', backref='sales')

    def __repr__(self):
        return f'<SaleItem {self.sale_item_id}>'


class User(db.Model):
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    customer_name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, default='user')
    customer = db.relationship('Customer', backref='users')

    def __repr__(self):
        return f'<User {self.username}>'


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    order_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.Text)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    customer = db.relationship('Customer', backref='orders')
    user = db.relationship('User', backref='orders')

    def __repr__(self):
        return f'<Order {self.order_id}>'


class OrderItem(db.Model):
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    item_amount = db.Column(db.Float, nullable=False)
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product', backref='orders')

    def __repr__(self):
        return f'<OrderItem {self.order_item_id}>'


class Warehouse(db.Model):
    warehouse_id = db.Column(db.Integer, primary_key=True)
    warehouse_name = db.Column(db.Text, nullable=False)
    warehouse_address = db.Column(db.Text)
    warehouse_phone_number = db.Column(db.Text)
    warehouse_email = db.Column(db.Text)

    def __repr__(self):
        return f'<Warehouse {self.warehouse_name}>'


class WarehouseItem(db.Model):
    warehouse_item_id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(
        db.Integer, db.ForeignKey('warehouse.warehouse_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    warehouse = db.relationship('Warehouse', backref='items')
    product = db.relationship('Product', backref='warehouses')

    def __repr__(self):
        return f'<WarehouseItem {self.warehouse_item_id}>'


class MonthlySales(db.Model):
    month = db.Column(db.Text, primary_key=True)
    sales = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    profit_margin = db.Column(db.Float, nullable=False)
    revenue_growth = db.Column(db.Float, nullable=False)
    profit_growth = db.Column(db.Float, nullable=False)
    revenue_per_sale = db.Column(db.Float, nullable=False)
    profit_per_sale = db.Column(db.Float, nullable=False)
    revenue_per_customer = db.Column(db.Float, nullable=False)
    profit_per_customer = db.Column(db.Float, nullable=False)
    revenue_per_product = db.Column(db.Float, nullable=False)
    profit_per_product = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<MonthlySales {self.month}>'


class InactiveAccount(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), primary_key=True)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, default='user')

    def __repr__(self):
        return f'<InactiveAccount {self.username}>'


class Delivery(db.Model):
    delivery_id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    delivery_status = db.Column(db.Text)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    order = db.relationship('Order', backref='deliveries')

    def __repr__(self):
        return f'<Delivery {self.delivery_id}>'


@app.route("/, methods=['GET','POST']")
def index():
    if (request.method == 'POST') and ('product_name' in request.form):
        product_name = request.form['product_name']
        new_product = Product(product_id=product_name)

        response = product_response(jsonify(message="Product Added succesfully", 200))

        return response

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/')
        except:
            response_fail = product_response(jsonify(message="There was an issue adding your product", 500))
            return response_fail

    if (request.method == 'POST') and ('warehouse_name' in request.form):
        warehouse_name = request.form['warehouse_name']
        new_warehouse = Warehouse(warehouse_id=warehouse_name)

        response = warehouse_response(jsonify(message="Warehouse Added succesfully", 200))

        try:
            db.session.add(new_warehouse)
            db.session.commit()
            return redirect('/')
        except:
            response_fail = warehouse_response(jsonify(message="There was an issue adding your warehouse", 500))
            return response_fail

    else:
        products = Product.query.all()
        warehouses = Warehouse.query.all()
        return render_template('index.html', products=products, warehouses=warehouses)


@app.route("/users/", methods=['GET', 'POST'])
def users():
    if (request.method == 'POST') and ('username' in request.form):
        customer_name = request.form['customer_name']
        username = bleach.clean(request.form['username'])
        password_hash = bleach.clean(request.form['password_hash'])
        role = request.form['role']

        hashed_password = bcrypt.hashpw(password_hash.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = Customer(user_id=customer_name, username=username,
                            password_hash=hashed_password, role=role)

        response = user_response(jsonify(message="User Added succesfully", 200))

        return response

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
        except:
            response_fail = user_response(jsonify(message="There was an issue adding your customer", 500))
            return response_fail

    if (request.method == 'POST') and ('password' in request.form):
        username = bleach.clean(request.form['username'])
        password_hash = bleach.clean(request.form['password_hash'])

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password_hash.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            return redirect('/users')
        else:
            return 'Invalid username or password'


if __name__ == "__main__":
    app.run()
