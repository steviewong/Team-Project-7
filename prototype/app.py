#imports
import requests, flask, flask_sqlalchemy, flask_login, numpy, dotenv, logging, oauthlib, flask_bcrypt, form
from getpass import getuser
from flask import Flask, Response, request, render_template, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_required, login_user, logout_user
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

#init login manager
login_manager = LoginManager()
login_manager.init_app(app)

#init database
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

#set up User class which will represent each dataset in the database
class User(db.Model):

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

#APP ROUTES
@app.route('/')
@app.route('/static/home')
def main():
    return render_template('moviegen.html')

@app.route('/toWatch')
def toWatch(user_id):
    movies = User.getMovies()
    return render_template('watchList.html', movies=movies)

@app.route('/static/moviegen')
def afterLogin():
    return render_template('moviegen.html')

@app.route('/editWatchlist')
def editWatchlist(user_id):
    movie = request.form.get('movieTitle')
    user.addMovie(movie)

#route to add new user to database
@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    if flask.request.method == 'POST':
        email = flask.request.form['email']
        moviesToWatch = ''
        
        db.session.add(User)
        db.session.commit()

        return render_template('moviegen.html')

    return render_template('createUser.html') #code for lines 22, 87-101 adapted from https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application


genres = ['action', 'comedy', 'drama', 'fantasy', 'horror', 'mystery', 'romance', 'science fiction', 'thriller', 'christmas']

@app.route('/')
def start():
	return render_template('moviegen.html')

@app.route('/search',methods = ['GET','POST'])
def getposter():

	if request.method == ['GET']:
		return render_template("./index.html")
	else:
		url = "https://imdb8.p.rapidapi.com/auto-complete"

		movie = request.form['movieTitle']
		x =movie.replace(' ','%20')

		querystring = {"q":movie}

		headers = {
		"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
		}

		response = requests.request("GET", url, headers=headers, params=querystring)

		responsej = response.json()

		img = responsej['d'][0]['i']['imageUrl']

		return render_template("./index.html", movie = img)

def posty(movie):
   
	url = "https://imdb8.p.rapidapi.com/auto-complete"

	x = movie.replace(' ','%20')

	querystring = {"q":movie}

	headers = {
		"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
	}

	response = requests.request("GET", url, headers=headers, params=querystring)
	responsej = response.json()['d'][0]['i']['imageUrl']
	
	return responsej

@app.route('/static/getmovie',methods= ['GET','POST'])
def getmovie():
    if request.method == ['POST']:
        all = recommend()
        movie = all[0]

        movie1 = movie[7:-1]
	
        url = "https://imdb8.p.rapidapi.com/title/get-base"
        querystring = {"tconst":movie1}

        headers = {
	        "X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
	        "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        moviename = response.json()['title']
        poster = posty(movie1)

        return render_template("moviegen.html", name=moviename, img=poster, )# movie = poster, weather = all[1])

def getWeather():
    genre = ''

    #api call to Weather api to get weather description and current temperature
    weatherUrl = 'https://simple-weather2.p.rapidapi.com/weather'

    weatherHeaders = {
        'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
        'X-RapidAPI-Host': 'simple-weather2.p.rapidapi.com'
        }
                
    querystring = {'location': 'Boston, USA'}

    weatherResponse = requests.request('GET', weatherUrl, headers=weatherHeaders, params=querystring) #code lines 84-93, with variable names edited, taken from RapidAPI listing for Yahoo Weather API at https://rapidapi.com/apishub/api/yahoo-weather5
    weatherResponseJ = weatherResponse.json()

    weatherCondition = weatherResponseJ['current_weather']['description']
    temp = weatherResponseJ['current_weather']['temperature']

    #series of conditionals to determine appropriate genre based on a combination of the month, temp, and weather condition
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


def recommend():
    num = randint(0,99)
    all = getWeather()
    genre = all[0]

    url = "https://imdb8.p.rapidapi.com/title/v2/get-popular-movies-by-genre"

    querystring = {"genre": genre, "limit":"100"}

    headers = {
		"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
		}

    response = requests.request("GET", url, headers=headers, params=querystring)

    movie = response.json()[num]

    return [movie, all[1]]

oauth = OAuth(app)
app.secret_key = '8GTNQ_L7HZX'

google = oauth.register(
    name = "google",
    client_id = '894336266651-jsc8utbf0qfqjc4vau0n0v1819lskl29.apps.googleusercontent.com',
    client_secret = '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',
    access_token_url = 'https://accounts.google.com/o/oauth2/token', # possibly wrong
    acess_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    client_kwargs = {'scope': 'openid profile email'},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)

@app.route('/login',methods = ['GET','POST'])
def login():
    redirect_uri = url_for('authorize', _external=True)
    google = oauth.create_client('google')
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo') # wrote this in video but was different in copy
    #resp.raise_for_status() - not in video, commented out for now
    user_info = resp.json()
    # # do something with the token and profile
    session['email'] = user_info['email']
    return redirect('/logged')
    
if __name__ == '__main__':
    app.debug = True
    app.run()
