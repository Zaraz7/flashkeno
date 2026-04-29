# -*- coding: utf-8 -*-
from flask import render_template
from app import app
from app.html_generator import HTMLGenerator

generator = HTMLGenerator()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', table_rows=generator.get_table_rows())

