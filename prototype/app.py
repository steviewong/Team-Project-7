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

    firstName = db.Column(db.String(30), nullable=True)
    lastName = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(20), nullable=False)
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
    return render_template('movieGen.html')

#@app.route('/login', methods = ['GET', 'POST'])
#def login():
#    form = LoginForm()
#    if form.validate_on_submit():
#        user = User.query.get(form.email.data)
#        if user:
#            if flask.bcrypt.check_password_hash(user.password, form.password.data):
#                login_user(user, remember=True)
#                return render_template('moviegen.html')
#            flask.flash('Incorrect password')
#    return render_template('login.html', form=form)

@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.home'))

@app.route('/toWatch')
@login_required
def toWatch(user_id):
    movies = User.getMovies()
    return render_template('watchList.html', movies=movies)

@app.route('/static/moviegen')
@login_required
def afterLogin():
    return render_template('moviegen.html')

@app.route('/editWatchlist')
@login_required
def editWatchlist():
    movie = request.form.get('movieTitle')
    current_user.addMovie(movie)

#route to add new user to database
@app.route('/createUser', methods=['GET', 'POST'])
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


genres = ['action', 'comedy', 'drama', 'fantasy', 'horror', 'mystery', 'romance', 'science fiction', 'thriller', 'christmas']

def hello():

    movie = getposter()
    #return '<h1>movie</h1>'
    return render_template('./index.html',movie = movie)

@app.route('/about/')
def about():
    return '<h3>This is a Flask web application.</h3>'

if __name__ == '__main__':
    app.debug = True
    app.run()

@app.route('/')
def start():
	return render_template("./index.html")


@app.route('/search',methods = ['GET','POST'])
def getposter():

	if request.method == ['GET']:
		return render_template("./index.html")
	else:
		url = "https://imdb8.p.rapidapi.com/auto-complete"

		movie = request.form['movieTitle']
		#movie = "home alone"
	#movie = input("Enter movie:")
	#print("Username is: " + movie)
#movie = "the shawshank redemption"


		x =movie.replace(' ','%20')

		querystring = {"q":movie}

		headers = {
		"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
		}

		response = requests.request("GET", url, headers=headers, params=querystring)

		responsej = response.json()

		#print(responsej)

		#print(responsej['d'][0]['i']['imageUrl'])

		actor = responsej['d'][0]
		print(actor)
		img = responsej['d'][0]['i']['imageUrl']
		print(img)

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

    
   


@app.route('/getmovie',methods= ['GET','POST'])
def getmovie():

    # if request.method == ['GET']:
    #     return('index.html')
    # else:

        all = recommend()
        movie = all[0]

        movie1 = movie[7:-1]

        print(movie1)


	
        url = "https://imdb8.p.rapidapi.com/title/get-base"
        querystring = {"tconst":movie1}

        headers = {
	"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
	"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        moviename = response.json()['title']
        print(response.json()['title'])
        

        poster = posty(movie1)

        return render_template("movierec.html", name = moviename)# movie = poster, weather = all[1])
   

	#route for if user selects weather option to generate movie

def getMovieForWeather(): #wrapper function to call both apis in order
    result = getWeather()
    movie = getMovie(result)
    return render_template('weather.html', movie=movie)


def getMovieForFilter(): #wrapper function to call the movie api based on filter input
    filter = request.form.get('genre')
    movie = getMovie(filter)
    return movie

def getWeather():
    #calls function to obtain current month
        month = getMonth()

        genre = ''

    #api call to Yahoo weather api to get weather description and current temperature
    
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
        if month == '12':
            if 'Snow' in weatherCondition or temp < 32:
                genre = genres[10]
        elif 'Sunny' in weatherCondition:
            genre = genres[random.choice(0, 1, 2, 3, 6)]
        elif 'Rain' or 'Showers' in weatherCondition:
            if temp > 60:
                genre = genres[random.choice(1, 2, 3, 5, 7)]
            else:
                genre = genres[random.choice(2, 4, 5, 7, 8)] 
        elif 'Snow' in weatherCondition:
            genre = genres[random.choice(3, 5, 6)]
        elif 'Cloudy' in weatherCondition:
            genre = genres[random.choice(0, 2, 5, 7, 8)]
        elif 'Storm' in weatherCondition:
            genre = genres[random.choice(0, 2, 4, 5, 8)]
        else:
            genre = genres[random.randint(0, 10)]
        
        return [genre,weatherCondition]


def recommend():
    num = random.randint(0,99)
    all = getWeather()
    genre = all[0]

    url = "https://imdb8.p.rapidapi.com/title/v2/get-popular-movies-by-genre"

    querystring = {"genre":genre,"limit":"100"}

    headers = {
			"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
				"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
					}

    response = requests.request("GET", url, headers=headers, params=querystring)

    

    option = response.json()[num]

    print(option)
    return [option,all[1]]

def getMonth():
    #api call to world clock api to get current month
    
        monthUrl = 'https://world-clock.p.rapidapi.com/json/est/now'

        monthHeaders = {
            'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
	        'X-RapidAPI-Host': 'world-clock.p.rapidapi.com'
            }

        monthResponse = requests.request('GET', monthUrl, headers=monthHeaders) #code lines 124-131, with variable names edited, taken from RapidAPI listing for World Clock at https://rapidapi.com/theapiguy/api/world-clock/
        monthResponseJ = monthResponse.json()

        month = monthResponseJ['currentDateTime'][5:7]

        return month

def getMovie(genre):
    #dictionary to connect movie genres to their associated id number in the api used
    movieIDs = {'action': 28, 'comedy': 35, 'drama': 18, 'fantasy': 14, 'horror': 27, 'mystery': 9648, 'romance': 10749, 'science fiction': 878, 'thriller': 53}
    id = movieIDs[genre]

    #list of holiday movies
    xmasOptions = ['the grinch', 'home alone', 'love actually', 'elf', 'miracle on 34th street', 'klaus', 'the nightmare before christmas', 'die hard',\
        'the polar express', 'four christmases']

    #api call to advanced movie search api to get a series of movies based on the genre input
    if request.method == 'GET':
        movieUrl = ''
        querystring = {}
        movieHeaders = {
            'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
	        'X-RapidAPI-Host': 'advanced-movie-search.p.rapidapi.com'
        }

        if genre == 'christmas':
            title = xmasOptions[str(random.randint(10))]
            movieUrl = 'https://advanced-movie-search.p.rapidapi.com/search/movie'
            querystring = {'query': title, 'page': '1'}
        else:
            movieUrl = 'https://advanced-movie-search.p.rapidapi.com/discover/movie'
            querystring = {'with_genres': id, 'page': str(random.randint(5))}

        response = requests.request('GET', movieUrl, headers=movieHeaders, params=querystring) #code lines 151-154, 158-159, 161-164, with variable names edited, taken from RapidAPI listing for Advanced Movie Search at https://rapidapi.com/jakash1997/api/advanced-movie-search
        movieOptions = response.json()

        #selects random movie from the list of options returned from api, or selects the appropriate christmas movie if relevant
        if genre == 'christmas':
            movie = movieOptions[0]
        else:
            movieNum = random.randint(len(movieOptions))
            movie = movieOptions[movieNum]

        #parses api return to find important information about movie
        movieTitle = movie['original_title']
        movieImage = movie['backdrop_path']

        genreIDs = movie['genre_ids']
        num = 0
        movieGenres = ''

        #search through dictionary to find each genre associated with chosen movie
        for i in genreIDs:
            for g in movieIDs:
                if movieIDs[g] == i:
                    movieGenres += genres[num], ", "
                num += 1

        movieDescription = movie['overview']

        #return most important info about movie
        return [movieTitle, movieImage, movieGenres, movieDescription]  

#@app.route('/weatherTest', methods = ['GET', 'POST'])
def weatherTest():
    #if flask.request.method == 'GET':	
        url = 'https://yahoo-weather5.p.rapidapi.com/weather'

        headers = {
                'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
                'X-RapidAPI-Host': 'yahoo-weather5.p.rapidapi.com'
                }
                
        querystring = {'location': 'boston,ma', 'format': 'json', 'u': 'f'}

        response = requests.request('GET', url, headers=headers, params=querystring) #code lines 39-48, with variable names edited, taken from RapidAPI listing for Yahoo Weather API at https://rapidapi.com/apishub/api/yahoo-weather5
        responseJ = response.json()

        weatherCond = responseJ['current_observation']['condition']['text']
        print(weatherCond)

        return render_template('weatherBoston.html', weatherCond=weatherCond)


