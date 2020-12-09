from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes_reports
from app.main import routes_users
from app.main import routes_tasks