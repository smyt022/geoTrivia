from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    #store the array of integer scores as a string array,
    #where the scores are separated by ","s
    allScores = models.TextField()

    currentScore = models.IntegerField(default=0) #keeps track of a game's current score
    #is reset to zero after the player's game ends (gets a question wrong)

    @property
    def intScoresArr(self):
        if not self.allScores: #if no scores (empty), return empty integer array
            return []
        else:
            strScoresArr = self.allScores.split(",")
            

            intScores = [int(score) for score in strScoresArr if score.strip()]
            return intScores

    @property
    def top_score(self):
        if not self.intScoresArr:#if no scores (empty array), return top score of zero
            return 0
        else:
            scores = self.intScoresArr
            top_score = 0#default is zero
            for score in scores:
                if score > top_score:
                    top_score = score
            return top_score
        
    @property
    def average_score(self):
        if not self.intScoresArr:#if no scores (empty array), return avg score 0
            return 0
        else:
            allScores = self.intScoresArr
            scoresSum = 0
            numOfScores = 0
            for score in allScores:
                numOfScores += 1
                scoresSum += score
            return scoresSum/numOfScores
        



