from flask import Flask, redirect, url_for, request, render_template, session
from flask_wtf import FlaskForm
from pymongo import MongoClient
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from api import *
import acp_times
import arrow
import flask
import os


app = Flask(__name__)

client = MongoClient("db", 27017)
db = client.tododb
DEFAULT_TOP = 20
TOKEN_EXPIRATION = 60 * 10     # Seconds
app.config['SECRET_KEY'] = "Name this language: '2' + '2' = '22'"


@app.route('/')
def todo():
    return render_template('calc.html')

@app.route('/login',methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username, password = form.username.data, form.password.data
        if True: #try:
            data = db.cred_db.find({"username":username})
            for d in data:
                profile_pw_hash = d["password"]
                if verify_password(password, profile_pw_hash):
                    session['token'] = generate_auth_token(d["profile_id"])
                    return  render_template("calc.html", status="Successful login",token=session['token'], username=username), 200

            return render_template("login.html",form=form ,status="Invalid username and password combination",token=""), 200                   # Couldn't find the
        else: #except
            return render_template("login.html",form=form, status="An error has occured.",token=""), 400

    return render_template("login.html", form=form)#, form=form)

@app.route('/logout',methods=['POST', 'GET'])
def logout():
    return render_template("calc.html", status="Logged out",token=""), 200

@app.route('/register',methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        username, password_raw = register_form.username.data, register_form.password.data
        profile_id = random.randint(10000000, 99999999)
        password = hash_password(password_raw)
        try:

            app.logger.debug(profile_id)

            data = db.cred_db.find({"username":username})
            for d in data:
                existing_username = d["username"]
                if existing_username == username:
                    return render_template("register.html", form=register_form, status="Username exists in database, please select another"), 401

            result = db.cred_db.insert({"username":username, "password":password, "profile_id":profile_id})
            return render_template("login.html", form=register_form, status="Registration Successful"), 200

        except:
            return "ERROR", 400
    return render_template("register.html", form=register_form)


###

@app.route('/clear',methods=['POST'])
def clear():
    db.tododb.delete_many({})
    return redirect(url_for('todo'))

@app.route('/save', methods=['POST'])
def new():
    data = {
        "opens" : request.form.getlist("open"),
        "close" : request.form.getlist("close"),
        "km" : request.form.getlist("km"),
    }

    for key in data.keys():
        data[key] = list(map(str, data[key]))
    app.logger.debug(data)

    for i in range(len(data["km"])):
        result = {"open":data["opens"][i], "close":data["close"][i], "km":data["km"][i]}
        if result["km"] != "":
            db.tododb.insert_one(result)

    return redirect(url_for('todo'))

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############

request_table = {
    "listAll": ["km", "open", "close"],
    "listOpenOnly": ["open"],
    "listCloseOnly": ["close"]
}

@app.route("/_disp_times", methods=['GET', 'POST'])
def _disp_times():
    """
    Gets information from VIEW in order to see what kind of
    query the user wants. Then returns JSON formatted data
    for the user.
    """
    fields = request.args.get('fields', type=str)
    format_type = request.args.get('format', type=str)
    top = request.args.get('top', type=int)
    token = request.args.get('token', type=str)
    results = {}

    result, length, code = retrieve(token, format_type, top, request_table[fields])
    return flask.jsonify(result=result, length=length, code=code)

    # elif code == 401: # Unauthorized
    #     app.logger.debug("Token Expired! Let's log the user out.")
    #     return render_template('calc.html')

@app.route("/_calc_times", methods=['GET', 'POST'])
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """

    app.logger.debug("Got a JSON request")

    km = request.args.get('km', 999, type=float)
    distance = request.args.get('distance', 200, type=int)
    begin_time = request.args.get('begin_time', type=str)
    begin_date = request.args.get('begin_date', type=str)

    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))

    print(begin_date + " " + begin_time)
    start_arrow = arrow.get(begin_date + " " + begin_time, "YYYY-MM-DD HH:mm")
    print('start', start_arrow.isoformat())

    open_time = acp_times.open_time(km, distance, start_arrow)
    close_time = acp_times.close_time(km, distance, start_arrow)
    result = {"open": open_time, "close": close_time}

    return flask.jsonify(result=result)


###############
### WTFORMS ###
###############


class LoginForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    password = StringField("Password", [validators.Length(min=4, max=50)])
    memorize = BooleanField("Remeber Me", [validators.Optional()])

class RegisterForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    password = StringField("Password", [validators.Length(min=4, max=50)])


#####################
### AUTHORIZATION ###
#####################


def retrieve(token, format = 'json', top = DEFAULT_TOP, fields = ["km", "open", "close"]):
    if verify_auth_token(token):
        if format == 'json':
            return retrieve_json(top, fields)
        else:
            return retrieve_csv(top, fields)
    else:
        return {}, 0, 401 # Unauthorized

def generate_auth_token(profile_id, expiration=TOKEN_EXPIRATION):
   s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
   return s.dumps({'profile_id': profile_id})

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False    # valid token, but expired
    except BadSignature:
        return False    # invalid token
    return True

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
