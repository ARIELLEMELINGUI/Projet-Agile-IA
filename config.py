from flask import Flask


import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///smart-backlog.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-en-prod")
JSON_SORT_KEYS = False
