from flask import Flask, render_template, redirect, url_for,request
import requests

import random
import time 
from getpass import getuser


app = Flask(__name__)

genres = ['action', 'comedy', 'drama', 'fantasy', 'horror', 'mystery', 'romance', 'science fiction', 'thriller', 'christmas']

def hello():

    movie = getposter()
    #return '<h1>movie</h1>'
    return render_template('./index.html',movie = movie)

@app.route('/about/')
def about():
    return '<h3>This is a Flask web application.</h3>'

# if __name__ == '__main__':
#     app.debug = True
#     app.run()

@app.route('/')
def start():
	return render_template("./index.html")


@app.route('/search',methods = ['GET','POST'])
def getposter():

	if request.method == ['GET']:
		return render_template("./filters.html")
	else:
		url = "https://imdb8.p.rapidapi.com/auto-complete"

		movie = request.form['movieTitle']
		#movie = "home alone"
	#movie = input("Enter movie:")
	#print("Username is: " + movie)
#movie = "the shawshank redemption"


		x = movie.replace(' ','%20')

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
        movieid = response.json()['id']
        print(response.json()['title'])
        

        poster = posty(movie1)

        return render_template("filters.html", name = moviename, link = "https://imdb.com" + movieid)# movie = poster, weather = all[1])
   

	#route for if user selects weather option to generate movie





def getMovieForWeather(): #wrapper function to call both apis in order
    result = getWeather()
    movie = getMovie(result)
    return render_template('weather.html', movie=movie)

@app.route('/getMovieForFilter')
def getMovieForFilter(): #wrapper function to call the movie api based on filter input
    filter = request.args.get('genre')
    print(filter)
    movie = getMovie(filter)
    return movie

def getWeather():
    #calls function to obtain current month
        month = getMonth()

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
            querystring = {'with_genres': id, 'page': str(random.randint(1,5))}

        response = requests.request('GET', movieUrl, headers=movieHeaders, params=querystring) #code lines 151-154, 158-159, 161-164, with variable names edited, taken from RapidAPI listing for Advanced Movie Search at https://rapidapi.com/jakash1997/api/advanced-movie-search
        movieOptions = response.json()

        #selects random movie from the list of options returned from api, or selects the appropriate christmas movie if relevant
        if genre == 'christmas':
            movie = movieOptions[0]
        else:
            print(movieOptions)
            movieNum = random.randint(0,len(movieOptions))
            movie = movieOptions['results'][movieNum]

        #parses api return to find important information about movie
        movieTitle = movie['original_title']
        movieImage = movie['backdrop_path']
        id = movie['id']

        genreIDs = movie['genre_ids']
        num = 0
        movieGenres = ''

        #search through dictionary to find each genre associated with chosen movie
        # for i in genreIDs:
        #     for g in movieIDs:
        #         if movieIDs[g] == i:
        #             movieGenres += genres[num], ", "
        #         num += 1

        movieDescription = movie['overview']
        movieDetails = {
            'title': movieTitle,
            'image': movieImage,
            'genres': genreIDs,
            'description': movieDescription,
            'id': id
        }

        #return most important info about movie
        return movieDetails  

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

if __name__ == '__main__':
    app.debug = True
    app.run()

recommend()
print()
print()
getmovie()

