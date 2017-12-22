# -*- coding: utf-8 -*-

from flask import Blueprint

bp = Blueprint('ranking', __name__)

from . import views
