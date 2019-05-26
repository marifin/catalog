from flask import Flask, render_template, request, redirect, \
                  jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, SportItem, User
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


# Connect to Database and create database session.
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery unique session token called state, to prevent
# anti-forgery request attacks.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is \
                                             already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # if user does not exist, create one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    print getUserID(data["email"])
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius:150px;\
                          -webkit-border-radius: 150px;\
                          -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Logged out successfully.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')
    else:
        response = make_response(json.dumps('Failed to revoke token \
                                            for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# JSON APIs to view Catalog Information
@app.route('/catalog/<int:catalog_id>/sport/JSON')
def catalogSportJSON(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(SportItem).filter_by(catalog_id=catalog_id).all()
    return jsonify(SportItems=[i.serialize for i in items])


@app.route('/catalog/<int:catalog_id>/sport/<int:sport_id>/JSON')
def sportItemJSON(catalog_id, sport_id):
    Sport_Item = session.query(SportItem).filter_by(id=sport_id).one()
    return jsonify(Sport_Item=Sport_Item.serialize)


@app.route('/catalog/JSON')
def catalogsJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs=[c.serialize for c in catalogs])


# Show all catalog sports
@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    items = session.query(SportItem).all()
    if 'username' not in login_session:
        picture = url_for('static', filename='blank_user.gif')
        return render_template('viewonlycatalogs.html', picture=picture,
                               catalogs=catalogs, items=items)
    else:
        username = login_session['username']
        picture = login_session['picture']
        return render_template('catalogs.html', username=username,
                               picture=picture, catalogs=catalogs, items=items)


# Add a new sport
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCatalog = Catalog(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newCatalog)
        flash('A new catalog %s was created successfully' % newCatalog.name)
        session.commit()
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newCatalog.html')


# Edit a catalog

@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
    catalogToDelete = session.query(Catalog).filter_by(id=catalog_id).one()
    if catalogToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to edit this catalog.\
              You can only edit a catalog that you created.', 4000)
        return redirect('/catalog')
    if request.method == 'POST':
        session.delete(catalogToDelete)
        session.commit()
        flash('%s Successfully Deleted' % catalogToDelete.name)

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
    numOfItems = len(items)
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    if 'username' not in login_session:
        picture = url_for('static', filename='blank_user.gif')
        return render_template('viewOnlySport.html', picture=picture,
                               items=items, catalogs=catalogs,
                               catalog=catalog, numOfItems=numOfItems)
    else:
        picture = login_session['picture']
        username = login_session['username']
        return render_template('sport.html', picture=picture,
                               username=username, items=items,
                               catalogs=catalogs, catalog=catalog,
                               numOfItems=numOfItems)


# Show a sport item description
@app.route('/catalog/<int:catalog_id>/sport/<int:sport_id>/',
           methods=['GET', 'POST'])
def showSportItem(catalog_id, sport_id):
    displayedItem = session.query(SportItem).filter_by(id=sport_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if 'username' not in login_session:
        picture = url_for('static', filename='blank_user.gif')
        username = ''
        return render_template('viewonlysportItem.html', picture=picture,
                               username=username, catalog=catalog,
                               sport_id=sport_id, item=displayedItem)
    else:
        picture = login_session['picture']
        username = login_session['username']
        return render_template('sportItem.html', picture=picture,
                               username=username, catalog=catalog,
                               sport_id=sport_id, item=displayedItem)


# Create a new sport item
@app.route('/catalog/<int:catalog_id>/sport/new/', methods=['GET', 'POST'])
def newSportItem(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')

    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    username = login_session['username']
    picture = login_session['picture']
    if request.method == 'POST':
        newItem = SportItem(name=request.form['name'],
                            description=request.form['description'],
                            catalog_id=catalog_id,
                            user_id=login_session['user_id']
                            )
        session.add(newItem)
        session.commit()
        message = flash('New %s Item Created Successfully' % (newItem.name))
        return redirect(url_for('showItem', picture=picture,
                                username=username, catalog_id=catalog_id,
                                message=message))
    else:
        return render_template('newSportItem.html', picture=picture,
                               username=username, catalog=catalog)


# Edit a sport item
@app.route('/catalog/<int:catalog_id>/sport/<int:sport_id>/edit',
           methods=['GET', 'POST'])
def editSportItem(catalog_id, sport_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    username = login_session['username']
    picture = login_session['picture']

    if 'username' not in login_session:
        return redirect('/login')

    # Check if user is original creator of item
    editedItem = session.query(SportItem).filter_by(id=sport_id).first()
    if editedItem.user_id != login_session['user_id']:
        flash('You are not authorized to edit this item.\
              You can only edit an item that you created.', 4000)
        return redirect('/catalog')

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Sport Item Successfully Edited')
        return redirect(url_for('showItem', username=username,
                                picture=picture, catalog_id=catalog_id))
    else:
        return render_template('editSportItem.html', username=username,
                               picture=picture, catalog_id=catalog_id,
                               sport_id=sport_id, item=editedItem)


# Delete a sport item
@app.route('/catalog/<int:catalog_id>/sport/<int:sport_id>/delete',
           methods=['GET', 'POST'])
def deleteSportItem(catalog_id, sport_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemToDelete = session.query(SportItem).filter_by(id=sport_id).one()
    username = login_session['username']
    picture = login_session['picture']
    if itemToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to delete this item.\
              You can only delete an item that you created.', 4000)
        return redirect('/catalog')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Sport Item Successfully Deleted')
        return redirect(url_for('showItem', username=username,
                                picture=picture, catalog_id=catalog_id))
    else:
        return render_template('deleteSportItem.html', username=username,
                               picture=picture, item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
