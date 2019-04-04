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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Show all catalog sports
@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    # if 'username' not in login_session:
    #     return render_template('publiccatalogs.html', catalogs=catalogs)
    # else:
    return render_template('catalogs.html', catalogs=catalogs)


# Add a new sport
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    # if 'username' not in login_session:
    #     return redirect('/login')
    if request.method == 'POST':
        newCatalog = Catalog(name=request.form['name'])
        session.add(newCatalog)
        flash('A new catalog %s was created successfully' % newCatalog.name)
        session.commit()
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newCatalog.html')


# Edit a catalog

@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    editedCatalog = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
            flash('Catalog edited successfully to %s' % editedCatalog.name)
            return redirect(url_for('showCatalogs'))
    else:
        return render_template('editCatalog.html', catalog=editedCatalog)


# Delete a catalog
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('%s Successfully Deleted' % catalogToDelete.name)
        session.commit()
        return redirect(url_for('showCatalogs', catalog_id=catalog_id))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)


# Show a category's items

@app.route('/catalog/<int:catalog_id>/')
@app.route('/catalog/<int:catalog_id>/sport/')
def showItem(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(SportItem).filter_by(
        catalog_id=catalog_id).all()
    return render_template('sport.html', items=items, catalog=catalog)


# Create a new sport item
@app.route('/catalog/<int:catalog_id>/sport/new/', methods=['GET', 'POST'])
def newSportItem(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        newItem = SportItem(name=request.form['name'], description=request.form[
                           'description'], catalog_id=catalog_id)
        session.add(newItem)
        session.commit()
        flash('New Sport %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showItem', catalog_id=catalog_id))
    else:
        return render_template('newSportItem.html', catalog_id=catalog_id)


# Edit a sport item

@app.route('/catalog/<int:catalog_id>/sport/<int:sport_id>/edit', methods=['GET', 'POST'])
def editSportItem(catalog_id, sport_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(SportItem).filter_by(id=sport_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Sport Item Successfully Edited')
        return redirect(url_for('showItem', catalog_id=catalog_id))
    else:
        return render_template('editSportItem.html', catalog_id=catalog_id, sport_id=sport_id, item=editedItem)


# Delete a sport item
@app.route('/catalog/<int:catalog_id>/sport/<int:sport_id>/delete', methods=['GET', 'POST'])
def deleteSportItem(catalog_id, sport_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemToDelete = session.query(SportItem).filter_by(id=sport_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Sport Item Successfully Deleted')
        return redirect(url_for('showItem', catalog_id=catalog_id))
    else:
        return render_template('deleteSportItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
