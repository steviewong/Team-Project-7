from flask import Flask, render_template, redirect, url_for,request, session
import requests
from os import environ as env
from urllib.parse import quote_plus, urlencode
import random

import time 
from getpass import getuser
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)

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
    #mail = dict(session).get('email',None)
    return render_template("./home.html")


@app.route('/logged')
def started():

    email = dict(session).get('email',None)

    return render_template("./moviegen.html", email = email)


def posty(movie):
   

    url = "https://imdb8.p.rapidapi.com/auto-complete"

		
    x =movie.replace(' ','%20')

    querystring = {"q":movie}

    headers = {
		"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
	}

    response = requests.request("GET",url, headers = headers, params=querystring)

	

    responsej = response.json() 

    if responsej['d'][0]['i']['imageUrl'] == None:
        return '<h2> Not a movie </h2>'
    
    img = responsej['d'][0]['i']['imageUrl']
    
    return img
@app.route('/search',methods = ['GET','POST'])
def getposter():
   

    url = "https://imdb8.p.rapidapi.com/auto-complete"
    movie = 0 
    movie = request.form['movieTitle']

    x =movie.replace(' ','%20')

    querystring = {"q":movie}

    headers = {
		"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
	}

    response = requests.request("GET",url, headers = headers, params=querystring)

	

    responsej = response.json() 
    if responsej['d'][0]['i']['imageUrl'] == None:
        return render_template('index.html')
    img = responsej['d'][0]['i']['imageUrl']
    actors = responsej['d'][0]['s']
    
    return render_template('/searchresult.html',movie = img, actors = actors)   
    

    
   


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
        
        print(response.json())
        poster = posty(movie1)

        return render_template("weather.html", name = moviename, movie = poster, weather = all[1])
   

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

    

        url = "https://simple-weather2.p.rapidapi.com/weather"

        querystring = {"location":"Boston,USA"}

        headers = {
	"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
	"X-RapidAPI-Host": "simple-weather2.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

 #code lines 84-93, with variable names edited, taken from RapidAPI listing for Yahoo Weather API at https://rapidapi.com/apishub/api/yahoo-weather5
        weatherResponseJ = response.json()

        weatherCondition = weatherResponseJ['current_weather']['description']
        temp = weatherResponseJ['current_weather']['temperature']

        #series of conditionals to determine appropriate genre based on a combination of the month, temp, and weather condition
        if month == '12':
            if 'Snow' in weatherCondition or temp < 32:
                genre = genres[9]
        elif 'Sunny' or 'Clear' in weatherCondition:
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

def recommendy(genre):
    num = random.randint(0,99)
    

    url = "https://imdb8.p.rapidapi.com/title/v2/get-popular-movies-by-genre"

    querystring = {"genre":genre,"limit":"100"}

    headers = {
			"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
				"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
					}

    response = requests.request("GET", url, headers=headers, params=querystring)

    

    option = response.json()[num]

    print(option)
    return option

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

@app.route('/filter',methods = ['GET','POST'])
def look_by_genre():


    
        genre = request.form['genre']

        movie = recommendy(genre)
        

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
        
        print(response.json())
        poster = posty(movie1)

        return render_template("weather.html", name = moviename, movie = poster, weather = '--')

    


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

@app.route('/logout', methods = ['GET','POST'])
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
