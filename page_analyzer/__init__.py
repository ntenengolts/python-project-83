import os
from flask import Flask
from dotenv import load_dotenv

from .app import index, add_url, show_url, show_urls, test # noqa: F401


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret')
DATABASE_URL = os.getenv('DATABASE_URL')

