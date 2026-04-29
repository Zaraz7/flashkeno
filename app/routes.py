# -*- coding: utf-8 -*-
from flask import render_template
from app import app
from app.html_generator import HTMLGenerator
from app.database import SiteDatabase

db = SiteDatabase("sites.db")

@app.route('/')
@app.route('/index')
def index():
    grouped_sites = db.get_sites_by_type()
    return render_template('index.html', grouped_sites=grouped_sites)

