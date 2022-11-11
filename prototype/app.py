import requests
from getpass import getuser
import flask
from flask import Flask, Response, request, render_template, redirect, url_for


import os, base64

app = Flask(__name__)

@app.route('/pic', methods =["GET"])
def getposter():

    if flask.request.method == 'GET':	
        url = "https://imdb8.p.rapidapi.com/auto-complete"
        movie = input("Enter movie:")
        
    #movie = "the shawshank redemption"

        x =movie.replace(' ','%20')

        querystring = {"q":movie}

        headers = {
		"X-RapidAPI-Key": "708e98d42bmsh2404d0ed0519532p16b192jsn9727845ce981",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

        responsej = response.json()

        print(responsej['d'][0]['i']['imageUrl'])

        return responsej['d'][0]['i']['imageUrl']



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
