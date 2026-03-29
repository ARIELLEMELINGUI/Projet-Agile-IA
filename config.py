from flask import Flask
import os
app = Flask(__name__)


SQLALCHEMY_DATABASE_URI = 'sqlite:///smart-backlog.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # attention à la faute de frappe


