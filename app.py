from flask import Flask, render_template, request, redirect, url_for
from flask import flash, make_response, jsonify, session as login_session
import random
import string
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, joinedload
from db_setup import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)
Bootstrap(app)

ID = json.loads(open('client_secrets.json', 'r', encoding='utf-8').read())
CLIENT_ID = ID['web']['client_id']
APPLICATION_NAME = "catalogApp"


engine = create_engine(
    'sqlite:///catalogapp.db',
    connect_args={'check_same_thread': False}
    )
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
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
    result = json.loads(h.request(url, 'GET')[1].decode())
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    print(credentials.access_token)

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' class="profile-image img-circle"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/logout')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = '''
    https://accounts.google.com/o/oauth2/revoke?token={}
    '''.format(access_token)
    print(url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        flash("You have been logged out.")
        return redirect(url_for('showCategories'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Create user when he logged in for the first time
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Return user object of a given user id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Return user id of a given email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Show all categories
@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = session.query(Category).all()
    items = session.query(CategoryItem).join
    (Category).order_by(desc(CategoryItem.id)).limit(9).all()
    return render_template(
        'categories.html',
        categories=categories, items=items
        )


# Show all items of a specific category
@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>/items')
def showItems(category_name):
    categories = session.query(Category).all()
    cat = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CategoryItem).filter_by(category_id=cat.id).join(Category).all()
    return render_template(
        'items.html',
        items=items,
        categories=categories,
        category_name=category_name
        )


# Read Catergory Item
@app.route(
    '/catalog/<string:category_name>/<string:item_name>',
    methods=['GET', 'POST']
    )
def showItem(category_name, item_name):
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    if request.method == 'POST':
        newItem = MenuItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'], course=request.form['coures'],
            restaurant_id=restaurant_id
            )
        session.add(newItem)
        session.commit()
        flash("category item has been added !")
        return redirect(url_for('showItems', category_name=category_name))
    else:
        return render_template(
            'item.html',
            item=item, category_name=category_name
            )


# Create Catergory Item
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newCategoryItem():
    # redirect user to login page of he is not logged in
    if 'username' not in login_session:
        return redirect('/login')
    else:
        categories_list = session.query(Category).all()
        if request.method == 'POST':
            newItem = CategoryItem(
                name=request.form['name'],
                description=request.form['description'],
                category_id=request.form['category'],
                user_id=login_session["user_id"]
                )
            session.add(newItem)
            session.commit()
            category = session.query(Category).filter_by(id=newItem.category_id).one()
            flash("Category item has been added")
            return redirect(url_for(
                'showItem',
                category_name=category.name, item_name=newItem.name)
            )
        else:
            return render_template(
                'newCategoryItem.html',
                categories=categories_list
                )


# Update Catergory Item
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editCategoryItem(item_name):
    # redirect user to login page of he is not logged in
    if 'username' not in login_session:
        return redirect('/login')
    else:
        item = session.query(CategoryItem).filter_by(name=item_name).join(Category).one()
        # prevent user from editig another user's item
        if(login_session['user_id'] != item.user_id):
            return render_template('403.html')
        else:
            categories_list = session.query(Category).all()
            if request.method == 'POST':
                item.name = request.form['name']
                item.description = request.form['description']
                item.category_id = request.form['category']
                session.add(item)
                session.commit()
                flash("Category item has been updated.")
                return redirect(url_for(
                    'showItem',
                    category_name=item.category.name, item_name=item.name)
                )
            else:
                return render_template(
                    'editCategoryItem.html',
                    item=item, categories=categories_list
                    )


# Delete Catergory Item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(item_name):
    # redirect user to login page of he is not logged in
    if 'username' not in login_session:
        return redirect('/login')
    else:
        itemToDelete = session.query(CategoryItem).filter_by(name=item_name).join(Category).one()
        # prevent user from deleteing another user's item
        if(login_session['user_id'] != itemToDelete.user_id):
            return render_template('403.html')
        else:
            if request.method == 'POST':
                session.delete(itemToDelete)
                session.commit()
                flash("Category item has been deleted.")
                return redirect(url_for('showCategories'))
            else:
                return render_template(
                    'deleteCategoryItem.html',
                    item=itemToDelete)


# List all categories
@app.route('/catalog/categories/JSON')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(category=[category.serialize for category in categories])


# List all category items
@app.route('/catalog/items/JSON')
def categoryItemJSON():
    items = session.query(CategoryItem).all()
    return jsonify(categoryItems=[item.serialize for item in items])


# List all categories with its items
@app.route('/catalog/JSON')
def allJSON():
    categories = session.query(Category).all()
    allCat = []
    for c in categories:
        tmpCategory = {'id': c.id, 'name': c.name, 'items': []}
        for i in c.items:
            itemsDict = {
                'id': i.id,
                'name': i.name,
                'description': i.description
            }
            tmpCategory['items'].append(itemsDict)
        allCat.append(tmpCategory)
    return jsonify(allCategories=allCat)


if __name__ == '__main__':
    app.secret_key = 'super_sekret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
