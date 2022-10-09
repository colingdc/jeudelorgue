# -*- coding: utf-8 -*-

from flask import render_template

from . import bp
from ..decorators import manager_required
from ..lang import ADMIN_DASHBOARD


@bp.route("/dashboard", methods=["GET"])
@manager_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        title=ADMIN_DASHBOARD
    )
