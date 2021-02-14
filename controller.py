from flask import Flask, render_template, request, jsonify, session,redirect
from flask_pymongo import PyMongo
from utils import regAlog, forecastU
from pycoingecko import CoinGeckoAPI
from sendemail import send_message
import random, datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/betsite_db"
mongo = PyMongo(app)
users = mongo.db.user
forecasts = mongo.db.forecasts
coingecko = CoinGeckoAPI()

@app.route('/')
def index():
    context = None
    if session.get('username') != None:
        context = session.get('username')
    forecasts_notstart = forecasts.find({'count' : 1})
    return render_template('index.html', user=context, forecast = forecasts_notstart)


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

        if not regAlog.checklength(username,5,30):
            obj = {
                'ok': False,
                'status' : 'The number of characters in the username is not allowed'
            }
            return jsonify(obj)

        if not regAlog.checklength(password,8,64):
            obj = {
                'ok': False,
                'status' : 'The number of characters in the password is not allowed'
            }
            return jsonify(obj)

        if not regAlog.checkpassword(password,repassword):
            obj = {
                'ok': False,
                'status' : 'The password is different from repeating the password'
            }
            return jsonify(obj)

        if not regAlog.emailvalidate(email):
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
                'countcast' : 3,
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
        return redirect('/register')


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

        if not regAlog.checklength(username,5,30):
            obj = {
                'ok': False,
                'status' : 'The number  of characters in the username is not allowed'
            }
            return jsonify(obj)

        if not regAlog.checklength(password,8,64):
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
        return redirect('/login')

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


@app.route('/forecast')
def forecast():
    if session.get('username') == None:
        return redirect('/')
    time = datetime.datetime.now()
    y = time.strftime("%Y")
    m = time.strftime("%m")
    d = time.strftime("%d")
    date = y + '-' + m + '-' + d
    lists = ['Bitcoin' , 'Ethereum' , 'Ripple', 'Litecoin' , 'Bitcoin Cash', 'Stellar', 'Uniswap' , 'Cardano']
    return render_template('forecast.html' , coin_list = lists, time = date)


@app.route('/forecast/set', methods=['GET', 'POST'])
def forecast_set():
    if session.get('username') == None:
        return redirect('/')

    if request.method == 'POST':
        coin = request.form['coin']
        guess = request.form['guess']
        date = request.form['date']
        money = request.form['money']
        username = session.get('username')
        score = users.find_one({'username' : username})

        if not forecastU.checkNull(date):
            obj= {
                'ok': False,
                'status' : 'Enter the date'
            }
            return jsonify(obj)

        if not forecastU.checkmoney(money):
            obj= {
                'ok': False,
                'status' : 'The minimum wage prerequisite is $ 5'
            }
            return jsonify(obj)

        if not forecastU.checkNull(guess):
            obj= {
                'ok': False,
                'status' : 'The prediction value is empty'
            }
            return jsonify(obj)

        if score['countcast'] <= 0:
            obj= {
                'ok': False,
                'status' : 'Your allowed number of predictions has expired'
            }
            return jsonify(obj)

        if score['money'] < int(money):
            obj= {
                'ok': False,
                'status' : 'Account balance is low'
            }
            return jsonify(obj)

        obj_bet = {
            'coin' : coin,
            'guess' : int(guess),
            'date' : date,
            'money' : int(money),
            'username' : username,
            'count' : 1,
            'users': []
        }

        forecasts.insert_one(obj_bet)
        users.update({'username' : username },
            {'$set':{'countcast' : score['countcast'] - 1,
                'money' : score['money'] - int(money)}
            })

        obj = {
            'ok' : True,
            'status' : 'create'
        }

        return jsonify(obj)

    else:
        return redirect('/forecast')


@app.route('/participation/<id>')
def participation(id):
    if session.get('username') != None:
        return redirect('/')

    requestuser = session.get('username')
    cast = forecasts.find_one({'_id' : id})
    getuser = users.find_one({'username' : username})

    if cast['username'] == requestuser:
        obj= {
            'ok': False,
            'status' : 'You can not participate yourself'
        }
        return jsonify(obj)


    money = getuser['money']
    price = cast['money']

    if money < price:
        obj= {
            'ok': False,
            'status' : 'Your money is not enough to participate in this forecast'
        }
        return jsonify(obj)

    return redirect('/login')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
