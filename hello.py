
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlite3 import Error
import sqlite3
import secrets
import os
import sys


# configure application
app = Flask(__name__)

# generate and a random secret key
app.secret_key = secrets.token_urlsafe(16)

# connect to sqlite3 and set a cursor
conn = sqlite3.connect('game.db')
db = conn.cursor()

# cerate database if not exists
def create_database():
    db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, login TEXT UNIQUE, password TEXT, teacher TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP)")

def create_database_points():
    db.execute("CREATE TABLE IF NOT EXISTS points (id INTEGER, level INTEGER, points INTEGER, date DATETIME DEFAULT CURRENT_TIMESTAMP) ")
# create a connection to sqlite3 database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    
# create points database if not exists
create_database_points()


@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/kursy')
def kursy():
    return render_template("kursy.html")

@app.route('/lektorzy')
def lektorzy():
    return render_template("lektorzy.html")

@app.route('/login', methods=["POST", "GET"])
def login():

    #forget any user_id
    #session.clear()
    
    # connect to sqlite3 and set a cursor
    conn = sqlite3.connect('game.db')
    db = conn.cursor()


    if request.method == "GET":
        if not session.get('logged_in'):
            return render_template("login.html")
        else:
            return render_template("play.html")
        
    else:
        
        #ensure username was submitted
        if not request.form.get("login"):
            return render_template("error.html", error="Adres email nie został wprowadzony")
        
        #ensure password was submitted
        if not request.form.get("password"):
            return render_template("error.html", error="Hasło nie zostało wprowadzone")
        
        #ensure username exists in database and password is correct

        db.execute("SELECT login FROM users WHERE login = :login", [request.form.get("login")])
        row = db.fetchone()
        if row is None:
            return render_template("login-error.html")

        #remember which user has logged in
        db.execute("SELECT id FROM users WHERE login = :login", [request.form.get("login")])
        row = db.fetchone()
        session["user_id"] = row[0]
        session['logged_in'] = True

        return redirect('/play')

    
@app.route('/logout')
def logout():
    session.clear()
    return render_template("index.html")

@app.route('/play')
def play():
    return render_template("play.html")

@app.route('/audio1_0', methods=["GET", "POST"])
def audio1_0():
    if request.method == "GET":
        return render_template("audio1_0.html")
    else:
        # connect to sqlite3 and set a cursor
        conn = sqlite3.connect('game.db')
        db = conn.cursor()
        # user's id
        #id = session.get('user_id')
        id = session["user_id"]
        # correct answer
        correct = "It is a test file of a new game"
        user_answer = request.form.get("audio1_0")

        points = 1
        level = 1

        # check if correct answer
        if correct == user_answer:
            db.execute("INSERT INTO points (id, level, points) VALUES (:id, :level, :points)", [id, level, points])
            conn.commit()

        return render_template("audio1_1.html")

@app.route('/audio1_1', methods=["GET", "POST"])
def audio1_1():
    if request.method == "GET":
        return render_template("audio1_1.html")
    else:
        # connect to sqlite3 and set a cursor
        conn = sqlite3.connect('game.db')
        db = conn.cursor()
        # user's id
        #id = session.get('user_id')
        id = session["user_id"]
        # correct answer
        correct = "It is a test file of a new game"
        user_answer = request.form.get("audio1_1")
        # check how many points the user has
        db.execute("SELECT * FROM points WHERE id = :id ", [id])
        row = db.fetchone()
        points = row[2]
        

        new_points = points + 1

        # check if correct answer
        if correct == user_answer:
            db.execute("UPDATE points SET points = :new_points WHERE id = :id", [new_points, id])
            conn.commit()

        return render_template("audio1_2.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    # connect to sqlite3 and set a cursor
    conn = sqlite3.connect('game.db')
    db = conn.cursor()

   
    if request.method == "GET":
        return render_template("register.html")
    else:
        if not request.form.get("username") or not request.form.get("confirm-username") :
            return render_template("register-error.html")
        if not request.form.get("new-password") or not request.form.get("confirm-new-password"):
            return render_template("register-error.html")
        if request.form.get("new-password") != request.form.get("confirm-new-password"):
            return render_template("register-error.html")
        
        # hash a password and declare needed variables
        password = generate_password_hash(request.form.get("new-password"))
        login = request.form.get("username")
        teacher = request.form.get("teacher")
        # check if username is available
        db.execute("SELECT login FROM users WHERE login = :login", [login])
        check_result = db.fetchone()
        # insert to database if available
        if check_result is not None:
            return render_template("login-exist.html")
        else:
            db.execute("INSERT INTO users (login, password, teacher) VALUES (:login, :password, :teacher)", [login, password, teacher])
            conn.commit()
        
        return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)