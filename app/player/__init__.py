# -*- coding: utf-8 -*-

from flask import Blueprint

bp = Blueprint('player', __name__)

from . import views
