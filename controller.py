from flask import Flask, render_template, request, jsonify, session
from flask_pymongo import PyMongo
from utils.registeralogin import util

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/betsite_db"
mongo = PyMongo(app)
users = mongo.db.user

@app.route('/')
def index():
    context = None
    if session.get('username') != None:
        context = session.get('username')
    return render_template('index.html', user=context)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register/set' , methods=['GET', 'POST'])
def register_set():
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']
        email = request.form['email']

        if not util.checklength(username,5,30):
            obj = {
                'ok': False,
                'status' : 'The number of characters in the username is not allowed'
            }
            return jsonify(obj)

        if not util.checklength(password,8,64):
            obj = {
                'ok': False,
                'status' : 'The number of characters in the password is not allowed'
            }
            return jsonify(obj)

        if not util.checkpassword(password,repassword):
            obj = {
                'ok': False,
                'status' : 'The password is different from repeating the password'
            }
            return jsonify(obj)

        if not util.emailvalidate(email):
            obj = {
                'ok': False,
                'status' : 'Invalid Email'
            }
            return jsonify(obj)

        obj_user = {
            'username' : username,
            'password' : password,
            'email' : email
        }
        users.insert_one(obj_user)
        obj = {
            'ok': True,
            'status' : 'sucssecful'
        }
        return jsonify(obj)
    else:
        return render_template('register.html')


@app.route('/login')
def login():
    if session.get('username') != None:
        return index()
    return render_template('login.html')

@app.route('/login/set' , methods=['GET', 'POST'])
def login_set():
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']

        user = users.find_one({'username' : username , 'password' : password})

        if not util.checklength(username,5,30):
            obj = {
                'ok': False,
                'status' : 'The number  of characters in the username is not allowed'
            }
            return jsonify(obj)

        if not util.checklength(password,8,64):
            obj = {
                'ok': False,
                'status' : 'The number of characters in the password is not allowed'
            }
            return jsonify(obj)

        if user != None:
            obj= {
                'ok': True,
                'values': {
                    'username' : username
                }
            }
            session['username'] = username
        else:
            obj= {
                'ok': False,
                'status' : 'Faild join'
            }
    else:
        return render_template('index.html')

    return jsonify(obj)


@app.route('/logout')
def logout():
    if session.get('username') != None:
        session['username'] = None

    return index()


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
