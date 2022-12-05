import requests
from getpass import getuser
import flask
import numpy
from flask import Flask, Response, request, render_template, redirect, url_for
from numpy.random import randint, choice


import os, base64

app = Flask(__name__, template_folder='.')

@app.route("/")
def main():
    return render_template('login.html')

@app.route('/weather', methods = ["GET"])
def getMovieForWeather():
    result = getWeather()
    #CALL TO IMDB API BASED ON GENRE RETURN

def getWeather():
    genre = ""
    genres = ['comedy', 'drama', 'science fiction', 'horror', 'western'\
        'thriller', 'action', 'fantasy', 'mystery', 'romance', 'christmas']

    if flask.request.method == 'GET':	
        weatherUrl = "https://yahoo-weather5.p.rapidapi.com/weather"

        weatherHeaders = {
                'X-RapidAPI-Key': '465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
                'X-RapidAPI-Host': 'yahoo-weather5.p.rapidapi.com'
                }
                
        querystring = {"location": 'boston,ma', "format": 'json', "u": 'f'}

        weatherResponse = requests.request("GET", weatherUrl, headers=weatherHeaders, params=querystring)
        weatherResponseJ = weatherResponse.json()

        weatherCondition = weatherResponseJ['current_observation']['condition']['text']
        
        temp =  weatherResponseJ['current_observation']['condition']['temperature']

            #DECIDE GENRE ASSOCIATIONS
        if "Sunny" in weather:
            genre = genres[randint(0, 7, 9)]
        elif weatherCondition == "Rain":
            if temp > 60:
                genre = genres[randint(1, 5, 8)]
            else:
                genre = genres[randint()] 
        else:
            genre = ""
        
        return genre


@app.route('/pic', methods =["GET"])
def getposter():

    if flask.request.method == 'GET':	
        url = "https://imdb-api.com/en/API/SearchTitle/{APIKey}/?genres=sci-fi                                    "
        movie = input("Enter movie:")
        
    #movie = "the shawshank redemption"

        x =movie.replace(' ','%20')

        querystring = {"q":movie}

        headers = {
		"X-RapidAPI-Key": "k_6n57pc5d",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

        responsej = response.json()

        print(responsej)

        #print(responsej['d'][0]['i']['imageUrl'])

        #return responsej['d'][0]['i']['imageUrl']

getWeather()

if __name__ == '__main__':
    app.run()

#movie = input("Enter movie:")
#print("Username is: " + movie)
#movie = "the shawshank redemption"


#x =movie.replace(' ','%20')



#code = "/auto-complete?q=" + x

#conn.request("GET", code, headers=headers)

#res = conn.getresponse()
#data = res.read()

#print(res.json())
#print(type(data))
#x =json.load(data)
#print(x['l'])


#print(data['l'])



#decoded = data.decode("utf-8")


# decoded

# main_response = data


# if "results" in main_response.body:
        
#     best_match = main_response.body["results"][0]
#     movie_id = best_match["id"][7:-1]  
            
#     movie_title = best_match["title"]
            
#     movie_year = str(best_match["year"])


# print(movie_year)
