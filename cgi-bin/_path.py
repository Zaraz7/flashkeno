import os
import sys

cgi_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(cgi_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from lib.html_generator import HTMLGenerator

print("Content-type: text/html\n<p>Da fuck u doing here</p>")