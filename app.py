from flask import Flask, request, render_template, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import db, Product, Customer
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/products/', methods=['GET', 'POST'])
def products():


if __name__ == '__main__':
    app.run(debug=True, port=3000)
