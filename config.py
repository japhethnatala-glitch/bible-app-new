import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallbacksecret")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
