from flask import Flask, render_template, request, jsonify, session,redirect
from flask_pymongo import PyMongo
from utils import regAlog, forecastU
from pycoingecko import CoinGeckoAPI
from sendemail import send_message
from startforesact import startbet
from forgetpassword import forget_message
from expireforecast import startDbet, endbet
import random, datetime, uuid

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/betsite_db"
mongo = PyMongo(app)
users = mongo.db.user
forecasts = mongo.db.forecasts
coingecko = CoinGeckoAPI()
timerruns = mongo.db.timerrun
lis=[]
timerruns.update({'status' : True},{'$set' : {'ids' : lis}})
startbet()
endbet()

@app.route('/')
def index():
    context = None
    if session.get('username') != None:
        context = session.get('username')
    forecasts_notstart = forecasts.find({'count' : 1})
    forecasts_start = forecasts.find({'count' : 2 , 'activate' : True})
    forecasts_end = forecasts.find({'count' : 2, 'activate' : False})
    return render_template('index.html', user=context, forecast_notstart = forecasts_notstart,
        forecasts_start = forecasts_start, forecasts_end = forecasts_end)


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
            forgetcode = uuid.uuid1()
            obj_user = {
                'username' : username,
                'password' : password,
                'email' : email,
                'score' : 0.0,
                'money' : 5.0,
                'countcast' : 3,
                'activate' : False,
                'code' : ran,
                'forgetpassword' : forgetcode.hex
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
        users.update({'username' : username , 'code' : code},{'$set':{'activate' : True}})

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
    lists = ['Bitcoin' , 'Ethereum' , 'Ripple', 'Litecoin' , 'Bitcoin-Cash', 'Stellar', 'Uniswap' , 'Cardano']
    return render_template('forecast.html' , coin_list = lists, time = date)


@app.route('/forecast/set', methods=['GET', 'POST'])
def forecast_set():
    if session.get('username') == None:
        return redirect('/')

    if request.method == 'POST':
        coin = request.form['coin']
        guess = request.form['guess']
        date = request.form['date']
        times = request.form['times']
        money = request.form['money']
        username = session.get('username')
        score = users.find_one({'username' : username})

        if not forecastU.checkNull(date):
            obj= {
                'ok': False,
                'status' : 'Enter the date'
            }
            return jsonify(obj)

        if not forecastU.checkNull(times):
            obj= {
                'ok': False,
                'status' : 'Enter the time'
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

        if score['money'] < float(money):
            obj= {
                'ok': False,
                'status' : 'Account balance is low'
            }
            return jsonify(obj)

        timeset = times.split(':')
        date = date + ('-' + timeset[0] + '-' + timeset[1])

        if not forecastU.checktime(date):
            obj= {
                'ok': False,
                'status' : 'The selected date is less than now'
            }
            return jsonify(obj)

        id = uuid.uuid1()
        datecast = datetime.datetime.now()

        
        obj_bet = {
            'id' : id.hex,
            'coin' : coin,
            'guess' : float(guess),
            'date' : date,
            'money' : float(money),
            'username' : username,
            'count' : 1,
            'expiredate' : datecast,
            'activate' : True,
            'users': None,
            'winner' : None,
            'loser' : None
        }

        forecasts.insert_one(obj_bet)
        users.update({'username' : username },
            {'$set':{'countcast' : score['countcast'] - 1,
                'money' : score['money'] - float(money)}
            })

        startDbet(obj_bet['id'])

        obj = {
            'ok' : True,
            'status' : 'create'
        }
        return jsonify(obj)

    else:
        return redirect('/forecast')


@app.route('/participation/set', methods=['GET', 'POST'])
def participation_set():
    if session.get('username') == None:
        obj= {
            'ok': False,
            'status' : 'Please login'
        }
        return jsonify(obj)

    if request.method == 'POST':
        id = request.form['idcast']
        requestuser = session.get('username')
        cast = forecasts.find_one({'id' : id})

        getuser = users.find_one({'username' : requestuser})


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

        if requestuser == cast['users']:
            obj= {
                'ok': False,
                'status' : 'You have participated in this prediction'
            }
            return jsonify(obj)


        forecasts.update({'id' : id },
            {'$set':{'users' : requestuser, 'count' : cast['count'] + 1}})

        users.update({'username' : requestuser},{'$set' : {'money' : money - price}})

        startbet()
        
        obj= {
            'ok': True,
            'status' : 'sucsses'
        }
        return jsonify(obj)
    else:
        return redirect('/')


@app.route('/profile/<username>')
def profile(username):

    if session.get('username') == None:
        return redirect('/')

    user = users.find_one({'username' : username})
    
    if user == None:
        return redirect('/')

    return render_template('profile.html' , user = user)


@app.route('/profile/<username>/getcount', methods=['GET', 'POST'])
def getcount(username):
    if session.get('username') == None:
        return redirect('/')

    user = users.find_one({'username' : username})
    score = user['score']
    countcast = user['countcast']
    ran = 0
    if score > 0 :
        ran = ((score * 20) / 1000) 
        countcast += ran
    else :
        obj = {
            'ok' : False,
            'status' : 'Your score is low for receiving'
        }
        return jsonify(obj)

    users.update_one({'username' : username},{'$set' : {'countcast' : countcast, 'score' : 0}})
    obj = {
            'ok' : True,
            'status' : 'You received the remaining ' + str(ran) + 'bets',
            'count' : countcast
        }

    return jsonify(obj)


@app.route('/forgetpassword')
def forget():
    return render_template('forgetpassword.html')


@app.route('/forgetpassword/send', methods=['GET', 'POST'])
def forgetpassword(methods=['GET', 'POST']):
    email = request.form['email']
    user = users.find_one({'email' : email})

    if not regAlog.emailvalidate(email):
            obj = {
                'ok': False,
                'status' : 'Invalid Email'
            }
            return jsonify(obj)

    if user != None:
        forget_message(email,user['forgetpassword'],user['username'])
        obj = {
            'ok' : True,
            'status' : 'A password recovery link has been sent to your email'
        }
        return jsonify(obj)
    else:
        obj = {
            'ok' : False,
            'status' : 'This email is not registered'
        }

    return jsonify(obj)


@app.route('/forgetpassword/<email>/<code>')
def forgetpasswordshow(email,code):
    user = users.find_one({'email' : email , 'forgetpassword' : code})
    if user == None:
        return redirect('/')
    return render_template('forgetpassword-privite.html' , user = user)


@app.route('/forgetpassword/<email>/<code>/set', methods=['GET', 'POST'])
def forgetpasswordset(email,code):
    user = users.find_one({'email' : email , 'forgetpassword' : code})
    if user == None:
        obj = {
            'ok': False,
            'status' : 'This link has been used before'
        }
        return jsonify(obj)
    
    password = request.form['password']
    repassword = request.form['repassword']

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

    forgetcode = uuid.uuid1()
    users.update_one({'email' : email , 'forgetpassword' : code},{'$set' : 
        {'password' : password,'forgetpassword': forgetcode.hex}})
    obj = {
            'ok': True,
            'status' : 'Your password has changed'
        }
    
    return jsonify(obj)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
  
