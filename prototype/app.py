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

#GLOBAL VARIABLES
genres = ['action', 'comedy', 'drama', 'fantasy', 'horror', 'mystery', 'romance', 'science fiction', 'thriller', 'christmas']

#init database directory
basedir = os.path.abspath(os.path.dirname(__file__))

#create app
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'8439e671181dca475dad24b8ce65141d94159f5b3d813de1eac19bc6aec638de'

#init database
db = SQLAlchemy(app)

#init OAuth
auth = OAuth(app)

#init login manager
#login_manager = LoginManager()
#login_manager.init_app(app)

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

#@login_manager.user_loader
#def load_user(username):
#    return User.get(username)

#routes to allow OAuth authorization using a Google account
@app.route('/google')
def google():
    AUTH_CLIENT_ID = os.environ.get('AUTH_CLIENT_ID')
    AUTH_CLIENT_SECRET = os.environ.get('AUTH_CLIENT_SECRET')

    AUTH_URL = 'https://accounts.google.com/.well-known/openid-configuration'

    auth.register(
        name = 'google'
        #client_id = AUTH_CLIENT_ID
        #client_secret = AUTH_CLIENT_SECRET
        #server_metadata_url = AUTH_URL
        #client_kwargs = {
            #'scope': 'openid email profile'
        #}
    )

    redirect = url_for('google_auth', _external = True)
    return auth.google.authorize_redirect(redirect)

@app.route('/google/auth')
def google_auth():
    accessToken = auth.google.authorize_access_token()
    user = auth.google.parse_id_token(accessToken)
    print(" Google User ", user)
    return redirect('/')                                #code for lines 59-84 taken from https://www.geeksforgeeks.org/oauth-authentication-with-flask-connect-to-google-twitter-and-facebook/

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

#route for home page - prompts user to login
@app.route('/')
def main():
    return render_template('moviegen.html')

#route for if user selects weather option to generate movie
@app.route("/static/getMovieForWeather", methods = ['GET', 'POST'])
def getMovieForWeather(): #wrapper function to call both apis in order
    result = getWeather(flask.request.method)
    print(result)
    movie = getMovie(result, flask.request.method)
    return render_template('weather.html', movie=movie)

@app.route("/static/getMovieForFilter", methods = ['GET', 'POST'])
def getMovieForFilter(): #wrapper function to call the movie api based on filter input
    filter = request.form.get('genre')
    movie = getMovie(filter)
    return movie

def getWeather(method):
    #calls function to obtain current month
    month = getMonth()

    genre = ''

    #api call to Yahoo weather api to get weather description and current temperature
    if method == 'POST':	
        weatherUrl = 'https://yahoo-weather5.p.rapidapi.com/weather'

        weatherHeaders = {
                'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
                'X-RapidAPI-Host': 'yahoo-weather5.p.rapidapi.com'
                }
                
        querystring = {'location': 'boston,ma', 'format': 'json', 'u': 'f'}

        weatherResponse = requests.request('GET', weatherUrl, headers=weatherHeaders, params=querystring) #code lines 133-142, with variable names edited, taken from RapidAPI listing for Yahoo Weather API at https://rapidapi.com/apishub/api/yahoo-weather5
        weatherResponseJ = weatherResponse.json()

        weatherCondition = weatherResponseJ['current_observation']['condition']['text']
        temp = weatherResponseJ['current_observation']['condition']['temperature']

        #series of conditionals to determine appropriate genre based on a combination of the month, temp, and weather condition
        if month == '12':
            if 'Snow' in weatherCondition or temp < 32:
                genre = genres[10]
        elif 'Sunny' in weatherCondition:
            possGenSunny = [0, 1, 2, 3, 6]
            genre = genres[choice(possGenSunny)]
        elif 'Rain' or 'Showers' in weatherCondition:
            if temp > 60:
                possGenRainHT = [1, 2, 3, 5, 7]
                genre = genres[choice(possGenRainHT)]
            else:
                possGenRainLT = [2, 4, 5, 7, 8]
                genre = genres[choice(possGenRainLT)] 
        elif 'Snow' in weatherCondition:
            possGenSnow = [3, 5, 6]
            genre = genres[choice(possGenSnow)]
        elif 'Cloudy' in weatherCondition:
            possGenCloudy = [0, 2, 5, 7, 8]
            genre = genres[choice(possGenCloudy)]
        elif 'Storm' in weatherCondition:
            possGenStorm = [0, 2, 4, 5, 8]
            genre = genres[choice(possGenStorm)]
        else:
            genre = genres[randint(0, 10)]

        return genre

def getMonth():
    #api call to world clock api to get current month
    if flask.request.method == 'GET':	
        monthUrl = 'https://world-clock.p.rapidapi.com/json/est/now'

        monthHeaders = {
            'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
	        'X-RapidAPI-Host': 'world-clock.p.rapidapi.com'
            }

        monthResponse = requests.request('GET', monthUrl, headers=monthHeaders) #code lines 173-180, with variable names edited, taken from RapidAPI listing for World Clock at https://rapidapi.com/theapiguy/api/world-clock/
        monthResponseJ = monthResponse.json()

        month = monthResponseJ['currentDateTime'][5:7]

        return month

def getMovie(genre, method):
    #dictionary to connect movie genres to their associated id number in the api used
    movieIDs = {'action': 28, 'comedy': 35, 'drama': 18, 'fantasy': 14, 'horror': 27, 'mystery': 9648, 'romance': 10749, 'science fiction': 878, 'thriller': 53}
    id = str(movieIDs[genre])

    #list of holiday movies
    xmasOptions = ['the grinch', 'home alone', 'love actually', 'elf', 'miracle on 34th street', 'klaus', 'the nightmare before christmas', 'die hard',\
        'the polar express', 'four christmases']

    #api call to advanced movie search api to get a series of movies based on the genre input
    if method == 'POST':
        movieUrl = ''
        querystring = {}
        movieHeaders = {
            'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
	        'X-RapidAPI-Host': 'advanced-movie-search.p.rapidapi.com'
        }

        if genre == 'christmas':
            title = xmasOptions[str(randint(10))]
            movieUrl = 'https://advanced-movie-search.p.rapidapi.com/search/movie'
            querystring = {'query': title, 'page': '1'}
        else:
            movieUrl = 'https://advanced-movie-search.p.rapidapi.com/discover/movie'
            querystring = {'with_genres': id, 'page': str(randint(5))}

        response = requests.request('GET', movieUrl, headers=movieHeaders, params=querystring) #code lines 200-203, 207-208, 210-213, with variable names edited, taken from RapidAPI listing for Advanced Movie Search at https://rapidapi.com/jakash1997/api/advanced-movie-search
        movieOptionsRaw = response.json()
        movieOptions = movieOptionsRaw['results']
        print(movieOptions)
        print(len(movieOptions))

        #selects random movie from the list of options returned from api, or selects the appropriate christmas movie if relevant
        if genre == 'christmas':
            movie = movieOptions[0]
        else:
            movieNum = randint(len(movieOptions))
            movie = movieOptions[movieNum]

        #parses api return to find important information about movie
        movieTitle = movie['original_title']
        movieImage = movie['backdrop_path']
        movieDescription = movie['overview']

        #return most important info about movie
        return [movieTitle, movieImage, genre, movieDescription]  

@app.route('/static/weatherTest', methods = ['GET', 'POST'])
def weatherTest():
    if flask.request.method == 'POST':	
        url = 'https://yahoo-weather5.p.rapidapi.com/weather'

        headers = {
                'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
                'X-RapidAPI-Host': 'yahoo-weather5.p.rapidapi.com'
                }
                
        querystring = {'location': 'boston,ma', 'format': 'json', 'u': 'f'}

        response = requests.request("GET", url, headers=headers, params=querystring) #code lines 39-48, with variable names edited, taken from RapidAPI listing for Yahoo Weather API at https://rapidapi.com/apishub/api/yahoo-weather5
        responseJ = response.json()

        weatherCond = responseJ['current_observation']['condition']['text']

        return render_template('weatherBoston.html', weatherCond=weatherCond)


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port=8000,
            threaded=True)    
