import os
from flask import Flask
from flask_cors import CORS
from blackfynn import Blackfynn
from service.config import Config

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
import service.routes as _unused

