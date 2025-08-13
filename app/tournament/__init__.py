from flask import Blueprint

bp = Blueprint('tournament', __name__)

from . import views
from .domain import get_tournament
