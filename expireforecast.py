from flask import Flask
from flask_pymongo import PyMongo
from pycoingecko import CoinGeckoAPI
import datetime, threading

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/betsite_db"
mongo = PyMongo(app)
users = mongo.db.user
forecasts = mongo.db.forecasts
    


def deletebet(id):
    getcast = forecasts.find_one({'id' : id})

    if getcast['count'] == 1:
        forecasts.delete_one({'id' : id})
        
    return


def startDbet(id):

    timer = threading.Timer(600,deletebet ,[id])
    timer.start()

    return 


def findbet():
    listid = []
    casts = forecasts.find()
    for count in casts:
        if count['count'] == 1 and count['activate'] == True:
            listid.append(count['id'])

    return listid


def endbet():
    for id in findbet():
        dateone = datetime.datetime.now()

        getcast = forecasts.find_one({'id' : id})

        datecast = getcast['expiredate']
        datecast += datetime.timedelta(minutes=10)

        if dateone > datecast : 
            forecasts.delete_one({'id' : id})

    return 