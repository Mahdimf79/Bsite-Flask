from flask import Flask
from flask_pymongo import PyMongo
from pycoingecko import CoinGeckoAPI
import datetime, threading

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/betsite_db"
mongo = PyMongo(app)
users = mongo.db.user
forecasts = mongo.db.forecasts
timerruns = mongo.db.timerrun
coingecko = CoinGeckoAPI()

def readybet():
    listid = []
    casts = forecasts.find()
    for count in casts:
        if count['count'] > 1 and count['activate'] == True:
            listid.append(count['id'])

    return listid


def timebet():
    listsec = []
    for id in readybet():
        dateone = datetime.datetime.now()

        getcast = forecasts.find_one({'id' : id})

        datecast = getcast['date'].split('-')

        checkmonth = datecast[1]

        if '0' in checkmonth:
            checkmonth = checkmonth[1]

        datetow = datetime.datetime(int(datecast[0]),int(checkmonth),int(datecast[2]),int(datecast[3]),
            int(datecast[4]))

        datestart = datetow - dateone

        listsec.append([id,datestart.seconds])


    return listsec


def checkprice(coin,id):
    getprice = coingecko.get_price(ids= coin, vs_currencies= 'usd')
    price = getprice[coin.lower()]['usd']

    cast = forecasts.find_one({'id' : id})
    userc = users.find_one({'username' : cast['users']})
    usero = users.find_one({'username' : cast['username']})
    guess = cast['guess']
    money = cast['money']
    scoreplus = userc['score'] + ((money*4) - 6)
    scoremin = usero['score'] - ((money*4) - 6)
    winer = ''
    loser = ''
    if guess != price:
        users.update_one({'username' : cast['users']},{'$set': {'money' : userc['money'] + (money*2),
            'score' : scoreplus}})

        users.update_one({'username' : cast['username']},{'$set': {'score' : scoremin}})
        winer = cast['users']
        loser = cast['username']
    else:
        users.update_one({'username' : cast['username']},{'$set': {'money' : usero['money'] + (money*2),
            'score' : usero['score'] + ((money*4) - 6)}})

        users.update_one({'username' : cast['users']},{'$set': {'score' : userc['score'] - ((money*4) - 6)}})
        winer = cast['username']
        loser = cast['users']

    forecasts.update_one({'id' : id},{'$set' : {'activate' : False, 'winner' : winer, 'loser' : loser}})


    return 


def startbet():
    listcast = timebet()
    timers = timerruns.find_one({'status' : True})
    timers = timers['ids']
    for start in listcast:
        if not start[0] in timers:
            cast = forecasts.find_one({'id' : start[0]})
            coin = cast['coin']
            secound = start[1]
            idl = timers
            idl.append(start[0])
            try:
                timer = threading.Timer(10,checkprice ,[coin,cast['id']])
                timer.start()
                timerruns.update_one({'status' : True},{'$set' : {'ids' : idl}})
            except:
                pass

    return 


