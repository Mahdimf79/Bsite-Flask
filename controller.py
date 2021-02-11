from flask import Flask, render_template, request, jsonify, session,redirect
from flask_pymongo import PyMongo
from utils.registeralogin import util
from sendemail import send_message
import random

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
    if session.get('username') != None:
        return redirect('/')
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

        user_check = users.find_one({'username' : username})
        email_check = users.find_one({'email' : email})
        if user_check == None and email_check == None:
            ran = random.randint(100000,999999)
            obj_user = {
                'username' : username,
                'password' : password,
                'email' : email,
                'score' : 0,
                'money' : 0,
                'activate' : False,
                'code' : ran
            }
            try:
                send_message(email,ran,username)
            except:
                obj = {
                    'ok': False,
                    'status' : 'There was a problem verifying the email'
                }
                return jsonify(obj)

            users.insert_one(obj_user)
            obj = {
                'ok': True,
                'status' : 'sucssecful'
            }
        else:
            obj = {
                'ok': False,
                'status' : 'Exists username or email'
            }
        return jsonify(obj)
    else:
        return render_template('register.html')


@app.route('/login')
def login():
    if session.get('username') != None:
        return redirect('/')
    return render_template('login.html')

@app.route('/login/set' , methods=['GET', 'POST'])
def login_set():
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']

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

        user = users.find_one({'username' : username , 'password' : password})

        if user != None:
            if user['activate'] == True:
                obj= {
                    'ok': True,
                    'values': {
                        'username' : user['username']
                    }
                }
                session['username'] = user['username']
            else:
                obj= {
                    'ok': False,
                    'status' : 'Your account is not activated. See your email'
                }
        else:
            obj= {
                'ok': False,
                'status' : 'Username or password is incorrect'
            }
    else:
        return render_template('index.html')

    return jsonify(obj)


@app.route('/logout')
def logout():
    if session.get('username') != None:
        session['username'] = None
    return redirect('/')


@app.route('/<username>/<int:code>')
def activate_user(username,code):
    user_check = users.find_one({'username' : username , 'code' : code})

    if user_check != None:
        user_active = users.update({'username' : username , 'code' : code},{'$set':{'activate' : True}})

    return render_template('activeuser.html' , user=user_check)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
