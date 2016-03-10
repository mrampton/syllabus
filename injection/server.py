#!/usr/bin/env python2.7

import os
import re
import time
import json
import md5
import pdb
import random
import psycopg2
import traceback

from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# XXX: set this to your database
#
DATABASEURI = "postgresql://injection:REALPASSWORD@localhost/injection"
#DATABASEURI = "sqlite:///test.db"

engine = create_engine(DATABASEURI)
engine.execute("""CREATE TABLE if not exists bad_table (
  id serial,
  name text
)""")

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    if hasattr(g, 'conn'):
      g.conn.close()
  except Exception as e:
    print e
    pass

@app.route('/', methods=["POST", "GET"])
def index():
  if request.method == "POST":
    name = request.form['name']
    q = "INSERT INTO bad_table(name) VALUES('%s');" % name
    print q
    g.conn.execute(q)

  cursor = g.conn.execute("SELECT * FROM bad_table limit 100")
  rows = cursor.fetchall()
  data = [ dict(zip(cursor.keys(), row)) for row in rows ]
  context = dict(data = data)
  return render_template("index.html", **context)


@app.route('/safe/', methods=["POST", "GET"])
def safe_index():
  if request.method == "POST":
    try:
      name = request.form['name']
      # Use ? for sqlite, %s for psycopg2
      # q = "INSERT INTO bad_table(name) VALUES(?);"
      q = "INSERT INTO bad_table(name) VALUES(%s);"
      print q
      g.conn.execute(q, (name,))
    except Exception as e:
      print e

  cursor = g.conn.execute("SELECT * FROM bad_table limit 100")
  rows = cursor.fetchall()
  data = [ dict(zip(cursor.keys(), row)) for row in rows ]
  context = dict(data = data)
  return render_template("index.html", **context)




if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
