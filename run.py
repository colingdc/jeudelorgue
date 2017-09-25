# -*- coding: utf-8 -*-

from app import create_app

app = create_app("config.BaseConfig")
app.run(debug = True)
