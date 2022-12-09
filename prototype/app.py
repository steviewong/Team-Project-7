#imports
import requests, flask, flask_sqlalchemy, flask_login, numpy, dotenv, logging, oauthlib, flask_bcrypt, form
from getpass import getuser
from flask import Flask, Response, request, render_template, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin #LoginForm, is_safe_url
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
login_manager.login_view = 'login.html'

#set up User class which will represent each dataset in the database
class User(UserMixin, db.Model):
    __tablename__ = 'Accounts'

    email = db.Column(db.String(50), primary_key=True)
    moviesToWatch = db.Column(db.Text)

    def __repr__(self):
        return f'<Logged in under {self.email}>'
    
    def get_id(self):
        return self.email

    def is_anonymous(self):
        return False

    def getMovies(self):
        return self.moviesToWatch
    
    def addMovie(self, movieTitle):
        self.moviesToWatch += movieTitle + '\n'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

#APP ROUTES
@app.route('/')
@app.route('/static/home')
def main():
    return render_template('moviegen.html')

@app.route('/static/toWatch')
def toWatch(user_id):
    current_user.addMovie('the matrix')
    movies = User.getMovies()
    return render_template('watchList.html', movies=movies)

@app.route('/editWatchlist')
def editWatchlist():
    movie = request.form.get('movieTitle')
    current_user.addMovie(movie)

#route to add new user to database
#@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        firstName = flask.request.form['firstName']
        lastName = flask.request.form['lastName']
        email = flask.request.form['email']
        password = flask.request.form['password']
        
        db.session.add(User)
        db.session.commit()

        return render_template('moviegen.html')

    return render_template('createUser.html') #code for lines 22, 87-101 adapted from https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

#route for if user selects weather option to generate movie
@app.route('/static/getMovieForWeather', methods = ['GET', 'POST'])
def getMovieForWeather(): #wrapper function to call both apis in order
    result = getWeather(flask.request.method)
    genre = result[0]
    movie = getMovieWithGenre(genre, flask.request.method)
    return render_template('weather.html', movieTitle=movie[0], movieImg=movie[1], genre=genre, movieDescription=movie[2], weather=result[1])

#route for if user selects filter option to generate movie
@app.route('/static/getMovieForFilter', methods = ['GET', 'POST'])
def getMovieForFilter(): #wrapper function to call the movie api based on filter input
    filter = request.form.get('genre')
    movie = getMovieWithGenre(filter, flask.request.method)
    return render_template('filter.html', movieTitle=movie[0], movieImg=movie[1], movieDescription=movie[2])

#route for if user chooses to search for a movie
@app.route('/static/getMovieSearch', methods = ['GET', 'POST'])
def getMovieForSearch():
    movieID = getMovieID(request.form('movieTitle'), flask.request.method)
    movie = getMovieWithID(movieID, flask.request.method)
    return render_template('search.html', movieTitle=movie[0], movieImg=movie[1], movieDescription=movie[2])

#function to access movie api with genre and return important info
def getMovieWithGenre(genre, method):
    if method == 'POST':
        num = randint(0,99)

        #api call to IMDB popular movies by genre api to get a random movie's details (title, image, description) given a genre
        movieUrl = 'https://imdb8.p.rapidapi.com/title/v2/get-popular-movies-by-genre'
        movieQuerystring = {'genre': genre, 'limit': '100'}
        movieHeaders = {
		    'X-RapidAPI-Key': '708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981',
		    'X-RapidAPI-Host': 'imdb8.p.rapidapi.com'
		    }

        response = requests.request('GET', movieUrl, headers=movieHeaders, params=movieQuerystring) #code lines 110-117, with variable names edited, taken from RapidAPI listing for IMDB at https://rapidapi.com/apidojo/api/imdb8/
        movieReturn = response.json()[num]
        movieID = movieReturn[7:-1]
        
        info = getMovieWithID(movieID, method)

        return info

#function to access movie api with id and return important info
def getMovieWithID(id, method):
    if method == 'POST':

        #api call to IMDB overview/details api to get movie details (title, image, description) given an id
        movieUrl = 'https://imdb8.p.rapidapi.com/title/get-overview-details'
        movieQuerystring = {'tconst': id, 'currentCountry': 'US'}
        movieHeaders = {
            'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
            'X-RapidAPI-Host': 'imdb8.p.rapidapi.com'
            }

        response = requests.request('GET', movieUrl, headers=movieHeaders, params=movieQuerystring) #code lines 128-135, with variable names edited, taken from RapidAPI listing for IMDB at https://rapidapi.com/apidojo/api/imdb8/
        responseJ = response.json()
        movieInfo = [responseJ['title']['title'], responseJ['title']['image']['url'], responseJ['plotOutline']['text']]
        return movieInfo

#function to access movie api with title and return id, which can be used to find more information
def getMovieID(movieTitle, method):
    if method == 'POST':

        #api call to IMDB auto-complete api to get movie ID given a title
        idUrl = 'https://imdb8.p.rapidapi.com/auto-complete'
        querystring = {'q': movieTitle}
        idHeaders = {
            'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
            'X-RapidAPI-Host': 'imdb8.p.rapidapi.com'
        }

        idResponse = requests.request('GET', idUrl, headers=idHeaders, params=querystring) #code lines 144-151, with variable names edited, taken from RapidAPI listing for IMDB at https://rapidapi.com/apidojo/api/imdb8/
        idResponseJ = idResponse.json()

        return idResponseJ['d']['0']['i']['id']

#function to access weather api and return important info
def getWeather(method):
    if method == 'POST':
        genre = ''

        #api call to Yahoo weather api to get weather description and current temperature
        weatherUrl = 'https://simple-weather2.p.rapidapi.com/weather'
        weatherHeaders = {
            'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
            'X-RapidAPI-Host': 'simple-weather2.p.rapidapi.com'
            }
        querystring = {'location': 'Boston, USA'}

        weatherResponse = requests.request('GET', weatherUrl, headers=weatherHeaders, params=querystring) #code lines 161-168, with variable names edited, taken from RapidAPI listing for Yahoo Weather API at https://rapidapi.com/apishub/api/yahoo-weather5
        weatherResponseJ = weatherResponse.json()

        weatherCondition = weatherResponseJ['current_weather']['description']
        temp = weatherResponseJ['current_weather']['temperature']

        #series of conditionals to determine appropriate genre based on a combination of the temp and weather condition
        if 'Sunny' or 'Clear' in weatherCondition:
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
            genre = genres[randint(0, 9)]
            
        return [genre, weatherCondition]

if __name__ == '__main__':
    app.run(debug=True)

