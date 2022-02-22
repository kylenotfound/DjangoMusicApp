from django.db import models

class Musicdata(models.Model):
    acousticness = models.FloatField(null=True)
    artists = models.TextField()
    danceability = models.FloatField(null=True)
    duration_ms = models.FloatField(null=True)
    energy = models.FloatField(null=True)
    explicit = models.FloatField(null=True)
    id = models.TextField(primary_key=True)
    instrumentalness = models.FloatField(null=True)
    key = models.FloatField(null=True)
    liveness = models.FloatField(null=True)
    loudness = models.FloatField(null=True)
    mode = models.FloatField(null=True)
    name = models.TextField()
    popularity = models.FloatField(null=True)
    release_date = models.IntegerField(null=True)
    speechiness = models.FloatField(null=True)
    tempo = models.FloatField(null=True)
    valence = models.FloatField(null=True)
    year = models.IntegerField(null=True)


