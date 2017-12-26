# -*- coding: utf-8 -*-

from app import create_app

app = create_app("config.ProductionConfig")
app.run()
