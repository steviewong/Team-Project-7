#imports
import requests, flask, flask_sqlalchemy, flask_login, numpy, dotenv, logging, oauthlib
from getpass import getuser
from flask import Flask, Response, request, render_template, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from oauthlib.oauth2 import WebApplicationClient
from wtforms import StringField, PasswordField, SubmitField
from numpy.random import randint, choice

import os, base64
from sqlalchemy.sql import func

#GLOBAL VARIABLE
genres = ['action', 'comedy', 'drama', 'fantasy', 'horror', 'mystery', 'romance', 'science fiction', 'thriller']

#init database directory
basedir = os.path.abspath(os.path.dirname(__file__))

#create app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'8439e671181dca475dad24b8ce65141d94159f5b3d813de1eac19bc6aec638de'

#init databse
db = SQLAlchemy(app)

#init login manager
login_manager = LoginManager()
login_manager.init_app(app)

#set up User class which will represent each dataset in the database
class User(flask_login.UserMixin, db.Model):
    username = db.Column(db.String(30), primary_key=True)
    firstName = db.Column(db.String(30), nullable=True)
    lastName = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    timeCreated = db.Column(db.DateTime(timezone=True), server_default=func.now())
    moviesToWatch = db.Column(db.Text)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(username):
    return User.get(username)

#route to add new user to database
@app.route('/createUser/', methods=['GET', 'POST'])
def createUser():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        firstName = flask.request.form['firstName']
        lastName = flask.request.form['lasstName']
        email = flask.request.form['email']
        password = flask.request.form['password']
        
        db.session.add(User)
        db.session.commit()

        return flask.redirect(url_for('moviegen'))

    return render_template('createUser.html') #code for lines 22, 87-101 adapted from https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

def hello():
    movie = getPoster()
    #return '<h1>movie</h1>'
    return render_template('./index.html', movie = movie)

@app.route('/')
def home():
	return render_template("home.html")

@app.route('/about')
def about():
    return '<h3>This is a Flask web application.</h3>'

#route for if user selects weather option to generate movie
@app.route('/static/getMovieForWeather', methods = ['GET', 'POST'])
def getMovieForWeather(): #wrapper function to call both apis in order
    result = getWeather()
    genre = result[0]
    movie = getMovieWithGenre(genre, flask.request.method)
    return render_template('weather.html', movieTitle=movie[0], movieImg=movie[1], genre=genre, movieDescription=movie[2], weather=result[1])

#route for if user selects filter option to generate movie
@app.route("/static/getMovieForFilter", methods = ['GET', 'POST'])
def getMovieForFilter(): #wrapper function to call the movie api based on filter input
    filter = request.form.get('genre')
    movie = getMovieWithGenre(filter, flask.request.method)
    return render_template('filter.html', movieTitle=movie[0], movieImg=movie[1], genre=filter, movieDescription=movie[2])

#route for if user chooses to search for a movie
@app.route('/static/getMovieSearch', methods = ['GET', 'POST'])
def getMovieForSearch():
    movieID = getMovieID()
    movie = getMovieWithID(movieID, flask.request.method)
    return render_template('search.html', movieTitle=movie[0], movieImg=movie[1], movieDescription=movie[2])

#function to access movie api with genre and return important info
def getMovieWithGenre(genre, method):
    if method == 'POST':
        num = randint(0,99)

        findMovieUrl = 'https://imdb8.p.rapidapi.com/title/v2/get-popular-movies-by-genre'
        findMovieQuerystring = {'genre': genre, 'limit': '100'}
        findMovieHeaders = {
		    "X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		    "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
		    }

        response = requests.request('GET', findMovieUrl, headers=findMovieHeaders, params=findMovieQuerystring)
        movieReturn = response.json()[num]
        movieID = movieReturn[7:-1]
        
        info = getMovieWithID(movieID, method)

        return info

#function to access movie api with id and return important info
def getMovieWithID(id, method):
    if method == 'POST':
        url = "https://imdb8.p.rapidapi.com/title/get-overview-details"
        querystring = {"tconst": id, 'currentCountry': 'US'}
        headers = {
            "X-RapidAPI-Key": "465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f",
            "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
            }

        response = requests.request('GET', url, headers=headers, params=querystring)
        responseJ = response.json()
        movieInfo = [responseJ['title'], responseJ['title']['image']['url'], responseJ['plotOutline']['text']]

        return movieInfo

#function to access movie api with title and return id, which can be used to find more information
def getMovieID(movieTitle):
    idUrl = 'https://imdb8.p.rapidapi.com/auto-complete'
    querystring = {'q': movieTitle}
    idHeaders = {
        'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
        'X-RapidAPI-Host': 'imdb8.p.rapidapi.com'
    }

    idResponse = requests.request('GET', idUrl, headers=idHeaders, params=querystring)
    idResponseJ = idResponse.json()

    return idResponseJ['d']['0']['i']['id']

#function to access weather api and return important info
def getWeather():
    genre = ''

    #api call to Yahoo weather api to get weather description and current temperature
    weatherUrl = 'https://yahoo-weather5.p.rapidapi.com/weather'
    weatherHeaders = {
        'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
        'X-RapidAPI-Host': 'yahoo-weather5.p.rapidapi.com'
        }
    querystring = {'location': 'boston,ma', 'format': 'json', 'u': 'f'}

    weatherResponse = requests.request('GET', weatherUrl, headers=weatherHeaders, params=querystring) #code lines 84-93, with variable names edited, taken from RapidAPI listing for Yahoo Weather API at https://rapidapi.com/apishub/api/yahoo-weather5
    weatherResponseJ = weatherResponse.json()

    weatherCondition = weatherResponseJ['current_observation']['condition']['text']
    temp = weatherResponseJ['current_observation']['condition']['temperature']

    #series of conditionals to determine appropriate genre based on a combination of the month, temp, and weather condition
    if 'Sunny' in weatherCondition:
        genre = genres[choice(0, 1, 2, 3, 6)]
    elif 'Rain' or 'Showers' in weatherCondition:
        if temp > 60:
            genre = genres[choice(1, 2, 3, 5, 7)]
        else:
            genre = genres[choice(2, 4, 5, 7, 8)] 
    elif 'Snow' in weatherCondition:
        genre = genres[choice(3, 5, 6)]
    elif 'Cloudy' in weatherCondition:
        genre = genres[choice(0, 2, 5, 7, 8)]
    elif 'Storm' in weatherCondition:
        genre = genres[choice(0, 2, 4, 5, 8)]
    else:
        genre = genres[randint(0, 9)]
        
    return [genre, weatherCondition]

if __name__ == '__main__':
    app.run(debug=True)

