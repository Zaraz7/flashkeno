#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from _path import HTMLGenerator, sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

generator = HTMLGenerator(
    db_path='db/sites.db',
    template_path='templates/index.html',
    output_path='index.html'
)


print("Content-type: text/html\n")
print(generator.generate_list())