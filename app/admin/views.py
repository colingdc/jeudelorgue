# -*- coding: utf-8 -*-

from flask import render_template

from ..decorators import manager_required
from ..lang import WORDINGS
from . import bp


@bp.route("/dashboard", methods=["GET"])
@manager_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        title=WORDINGS.MAIN.ADMIN_DASHBOARD
    )
