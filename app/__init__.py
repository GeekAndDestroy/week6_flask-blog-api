from flask import Flask # Import the Flask class from the flask module
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Create an instance of Flask called app that will be the central object
app = Flask(__name__)
#set the configuration for the app
app.config.from_object(Config)

# create an instance of SQLAlchemy called db which will be the central object for our database

db = SQLAlchemy(app)
# create an instanmce of Migrate with the app and db
migrate = Migrate(app, db)

# import the routes to the app
from app import routes, models
