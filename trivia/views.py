#imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #decorator that can be used for some views functions
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *

import requests #for external APIs
import random #for shuffling the questions around

# Create your views here.
def index(request):
    #get top 3 users in a list
    top_players = sorted(User.objects.all(), key=lambda user: user.top_score, reverse=True)[:3]
    
    return render(request, "trivia/leaderBoard.html", {
        "topPlayers": top_players,
    })


def play(request):
    user = request.user 
    #check if answer was incorrect or correct
    #if incorrect, reset currentScore, and render "game over screen"

    #get a trivia question form the API
    url = "https://opentdb.com/api.php?amount=1&category=22&difficulty=easy&type=multiple"
    
    response_code = 1 #make it wrong at first so it goes in the loop

    #get request and request again if unsuccessful
    while response_code != 0:
        response = requests.get(url)
        if response.status_code == 200:
            #parse the JSON response
            data = response.json()
            #Extract information
            response_code = data["response_code"]
        else: #make response code wrong to redo
            response_code = 1

    question = data["results"][0] #theres only one question we asked for in the request
    print(question)#TESTING
    #get list of possible answers
    allAnswers = question['incorrect_answers'] + [question['correct_answer']]
    random.shuffle(allAnswers)

    #render with trivia question info
    return render(request, "trivia/play.html",{
        "apiWorking": "True",
        "questionText": question['question'],
        "correctAnswer": question['correct_answer'],
        "allAnswers": allAnswers
    })

def handlePlayerResponse(request, selection):
    user = request.user
    #check if correct or incorrect
    if selection == "correct":
        #increase currentScore
        user.currentScore += 1
        user.save()

        #redirect to play again
        return HttpResponseRedirect(reverse('play'))

    else: # selection == "incorrect":
        #add currentScore to the allScores string seperated by ","
        user.allScores = user.allScores+str(user.currentScore)+","
        #reset currentScore to zero
        playerScore = user.currentScore
        user.currentScore = 0
        user.save()

        #redirect to game over screen
        return render(request, "trivia/gameOver.html", {
            "playerScore": playerScore
        })

def profile(request):

    profile_user = request.user
    top_score = profile_user.top_score
    avg_score = profile_user.average_score
    print("allScores: "+profile_user.allScores) #TESTING


    return render(request, "trivia/profile.html", {
        "top_score": str(top_score),
        "avg_score": str(avg_score)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "trivia/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "trivia/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "trivia/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "trivia/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "trivia/register.html")

