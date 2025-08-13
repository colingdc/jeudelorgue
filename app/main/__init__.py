from flask import Blueprint

from ..models import Permission

bp = Blueprint('main', __name__)


@bp.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


from . import views, errors
