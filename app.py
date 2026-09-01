
from flask import *
import sqlite3

from next import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def sensor():
    data("GOOG")
    data("ADANIPOWER.NS")
    data("AAPL")


app = Flask(__name__)
app.secret_key = "secret key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/logon')
def logon():
    return render_template('signup.html')

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def eduspheresendmail(receiver_email):
    
    sender = "stockmarketgraph@gmail.com"
    password = "rxzpuzpohrpxvssb"   # NOT your normal password

    body = """Hi,
Greetings from Stock Prediction.

Please find attached stock charts.

Thank you.
"""

    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver_email
    message['Subject'] = 'Stock Prediction Data'

    message.attach(MIMEText(body, 'plain'))

    # Attach multiple files
    files = ["AAPL.png", "ADANIPOWER.NS.png", "GOOG.png"]

    for file in files:
        path = os.path.join("static", file)
        
        with open(path, "rb") as attachment:
            payload = MIMEBase('application', 'octet-stream')
            payload.set_payload(attachment.read())

        encoders.encode_base64(payload)
        payload.add_header('Content-Disposition', f'attachment; filename={file}')
        message.attach(payload)

    try:
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender, password)

        session.sendmail(sender, receiver_email, message.as_string())
        session.quit()

        print("✅ Mail Sent Successfully")

    except Exception as e:
        print("❌ Error:", e)

@app.route("/signup", methods=["post"])
def signup():
    username = request.form['user']
    name = request.form['name']
    email = request.form['email']
    number = request.form["mobile"]
    password = request.form['password']
    role = "student"
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`,'role') VALUES (?, ?, ?, ?, ?,?)",
                (username, email, password, number, name, role))
    con.commit()
    con.close()
    return render_template("index.html")


@app.route("/mail", methods=["post"])
def mail():
    r = request.form["email"]
    eduspheresendmail(r)
    x = pd.read_csv("processednew.csv")
    x = x.values.tolist()
    print(x)
    return render_template("home.html", e=x[1:])


@app.route("/signin", methods=["post"])
def signin():
    mail1 = request.form['user']
    password1 = request.form['password']
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute(
        "select `user`, `password`,role from info where `user` = ? AND `password` = ?", (mail1, password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signup.html")
    elif mail1 == str(data[0]) and password1 == str(data[1]):
        session['username'] = data[0]
        x = pd.read_csv("processednew.csv")
        x = x.values.tolist()
        print(x)
        return render_template("home.html", e=x[1:])
    else:
        return render_template("signup.html")


@app.route('/logout')
def home():
    session.pop('username', None)
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
