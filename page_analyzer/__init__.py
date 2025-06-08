import os
from flask import Flask
from dotenv import load_dotenv


load_dotenv()

app = Flask(name)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret')
DATABASE_URL = os.getenv('DATABASE_URL')


from . import app as routes
