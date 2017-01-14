#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'myrousz'

import time
import json, codecs
import os, cherrypy
import tempfile
import sqlite3
import uuid, shutil
import xlrd
from shutil import copyfile
from copy import deepcopy
from subprocess import Popen, PIPE
from cherrypy.lib.static import serve_file
from cherrypy.lib.httputil import parse_query_string
from cherrypy import tools
from openpyxl import load_workbook
from jinja2 import Environment, FileSystemLoader

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")
import csv
import unicodedata


env = Environment(loader=FileSystemLoader('templates'))

"""
import argparse
parser = argparse.ArgumentParser()
args = parser.parse_args()
"""


class Root:
    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render()

"""
    @cherrypy.expose
    @tools.json_in()
    @tools.json_out()
    def json(self, **kwargs):
        data = cherrypy.request.json
        filter = data["filter"]
        selected = data["selected"]
        expanded = data["expanded"]
        return get_index(filter, selected, expanded)
"""


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
                            'log.error_file': 'site.log',
                            'log.screen': True,
                            'tools.staticdir.on': True,
                            'tools.staticdir.dir': os.path.join(current_dir, "www")})
    cherrypy.config.update({'server.socket_port': 3333})
    root = Root()
    cherrypy.quickstart(root, '/')
