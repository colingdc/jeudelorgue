from flask import Blueprint

bp = Blueprint('tournament', __name__)

from . import views
