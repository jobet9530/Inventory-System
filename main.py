from flask import Flask, request, render_template, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import db, Product
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=3000)
