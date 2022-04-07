import os
import logging
from flask import Flask
from logging.handlers import RotatingFileHandler

def configure_logging(log_folder):
    if not log_folder:
        return
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    logfile = os.path.join(log_folder, 'autoquiz.log')
    logging.basicConfig(level=logging.INFO)
    handler = RotatingFileHandler(
        logfile, maxBytes=1024*1000, backupCount=5, encoding='UTF-8')
    fmt = logging.Formatter(
        '[%(levelname)s] %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(fmt)
    logging.getLogger().addHandler(handler)

def create_app():
    app = Flask(__name__)
    from . import api
    from .config import LOG_PATH
    configure_logging(LOG_PATH)
    app.register_blueprint(api.bp)
    return app
