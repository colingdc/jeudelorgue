# -*- coding: utf-8 -*-

from flask import render_template
# from flask import current_app, flash
from . import main
# from ..email import send_email


@main.route("/")
@main.route("/index")
def index():
    title = "Accueil"
    # if current_app.config["ADMIN_JDL"]:
    #     send_email(to = current_app.config["ADMIN_JDL"],
    #                subject = "Hello",
    #                template = "email/hello",
    #                user = "user123")
    #     flash("An email was sent")
    return render_template("main/index.html", title = title)
