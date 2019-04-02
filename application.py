from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, SportItem
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all catalog sports
@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    # if 'username' not in login_session:
    #     return render_template('publicrestaurants.html', restaurants=restaurants)
    # else:
    return render_template('catalogs.html', catalogs=catalogs)


# Show a category's items

@app.route('/catalog/<int:catalog_id>/')
@app.route('/catalog/<int:catalog_id>/sport/')
def showItem(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(SportItem).filter_by(
        catalog_id=catalog_id).all()
    return render_template('sport.html', items=items, catalog=catalog)


if __name__ == '__main__':
    #app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
