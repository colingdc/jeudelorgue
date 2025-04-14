from flask import Blueprint

bp = Blueprint('tournament_category', __name__)

from . import views
