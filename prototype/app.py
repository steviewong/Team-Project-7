import requests
from getpass import getuser
import flask
import numpy
from flask import Flask, Response, request, render_template, redirect, url_for
from numpy.random import randint, choice

import os, base64

#CHECK LINES NOTED IN CITATION COMMENTS

app = Flask(__name__, template_folder='.')

@app.route("/")
def main():
    return render_template('login.html')

@app.route('/weather', methods = ["GET"])
def getMovieForWeather():
    result = getWeather()
    #CALL TO IMDB API BASED ON GENRE RETURN

def getWeather():
    month = getMonth()

    genre = ""
    genres = ['comedy', 'drama', 'science fiction', 'horror', 'thriller',\
        'action', 'fantasy', 'mystery', 'romance', 'christmas']

    if flask.request.method == 'GET':	
        weatherUrl = "https://yahoo-weather5.p.rapidapi.com/weather"

        weatherHeaders = {
                'X-RapidAPI-Key': '465b9bba02m--sh9ec7cc598f38c88p193583jsn4b7a43cc9d7f',
                'X-RapidAPI-Host': 'yahoo-weather5.p.rapidapi.com'
                }
                
        querystring = {"location": 'boston,ma', "format": 'json', "u": 'f'}

        weatherResponse = requests.request("GET", weatherUrl, headers=weatherHeaders, params=querystring)
        weatherResponseJ = weatherResponse.json()

        weatherCondition = weatherResponseJ['current_observation']['condition']['text']
        
        temp =  weatherResponseJ['current_observation']['condition']['temperature']

        if month == "12":
            if "Snow" in weatherCondition or temp < 32:
                genre = genres[10]
        elif "Sunny" in weatherCondition:
            genre = genres[choice(0, 1, 5, 6, 8)]
        elif "Rain" in weatherCondition:
            if temp > 60:
                genre = genres[choice(0, 1, 2, 6, 7)]
            else:
                genre = genres[choice(1, 2, 3, 4, 7)] 
        elif "Snow" in weatherCondition:
            genre = genres[randint(6, 9)]
        elif "Cloudy" in weatherCondition:
            genre = genres[choice(1, 2, 4, 5, 7)]
        elif "Storm" in weatherCondition:
            genre = genres[choice(1, 3, 4, 5, 7)]
        else:
            genre = genres[randint(0, 10)]
        
        return genre

def getMonth():
    if flask.request.method == 'GET':	
        monthUrl = "https://world-clock.p.rapidapi.com/json/est/now"

        monthHeaders = {
            "X-RapidAPI-Key": "465b9bba02msh9ec7cc598f38c88p193583jsn4b7a43cc9d7f",
	        "X-RapidAPI-Host": "world-clock.p.rapidapi.com"
            }

        monthResponse = requests.request("GET", monthUrl, headers=monthHeaders) #code lines 64-71, with variable names edited, taken from RapidAPI listing for World Clock at https://rapidapi.com/theapiguy/api/world-clock/
        monthResponseJ = monthResponse.json()

        month = monthResponseJ['currentDateTime'][5:7]

        return month

@app.route('/pic', methods =["GET"])
def getMovie():

    if flask.request.method == 'GET':	
        url = "https://imdb-api.com/en/API/SearchTitle/{APIKey}/?genres=sci-fi"
    
        x = movie.replace(' ','%20')

        querystring = {"q":movie}

        headers = {
		"X-RapidAPI-Key": "k_6n57pc5d",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        responsej = response.json()

    return render_template('result.html', poster_url=responsej)    

if __name__ == '__main__':
    app.run()    
