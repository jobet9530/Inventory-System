from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from database import database
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, port=3300)
