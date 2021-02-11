from flask_mail import Mail, Message
from flask import Flask,redirect

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'betsite.everlice@gmail.com'
app.config['MAIL_PASSWORD'] = '1379m9731m:'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

def send_message(email_sent,code,user):
    link = "http://127.0.0.1:5000/" + user + "/"+ str(code)
    msg = Message('Welcome to Betsite', sender = 'betsite.everlice@gmail.com', recipients = [email_sent])
    msg.html = "<h2>Hello " + str(user) + "</h2><h3>your authentication link is at the bottom</h3><a href=' " + link + "'>Click me</a>"
    mail.send(msg)
    return redirect('/')
