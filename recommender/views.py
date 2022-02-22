from cgitb import text
from re import A
from recommender.forms import SearchForm
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.contrib import messages
from .models import *
from .forms import *
from django.views.decorators.http import require_POST, require_GET
import random
import requests
import json


def find_albums(artist, song_name = None, from_year = None, to_year = None):
    query = Musicdata.objects.filter(artists__contains = artist)
    if from_year is not None:
      query = query.filter(year__gte = from_year)
    if to_year is not None:
      query = query.filter(year__lte = to_year)
    if song_name is not None:
      query = query.filter(name__contains=song_name)
    return list(query.order_by('-popularity').values('id','name','year'))
    

@require_POST
def searchform_post(request):
    # create a form instance and populate it with data from the request:
    form = SearchForm(request.POST)
    # check whether it's valid:
    if form.is_valid():
        # process the data in form.cleaned_data as required
        from_year = None if form.cleaned_data['from_year'] == None else int(form.cleaned_data['from_year'])
        to_year = None if form.cleaned_data['to_year'] == None else int(form.cleaned_data['to_year'])
        albums = find_albums(
                form.cleaned_data['artist'],
                form.cleaned_data['song_name'],
                from_year,
                to_year
            )
        
        # Random 3 of top 10 popular albums
        answer = albums[:10]
        random.shuffle(answer)
        
        if request.user.is_authenticated:
          print(len(answer))
          if (len(answer) < 10): 
            answer = searchSpotify(request, form)
            if not answer == None:
              random.shuffle(answer)

        answer = list(answer)[:3]

        return render(request, 'recommender/searchform.html', {'form': form, 'albums': answer })
    else:
        raise Http404('Something went wrong')


def searchSpotify(request, form):
  if not request.user.is_authenticated:
    return None

  social = request.user.social_auth.get(provider='spotify')
  token = social.extra_data['access_token']
  query_string = form.cleaned_data['artist'] + ' ' + form.cleaned_data['song_name'] + ' ' + form.cleaned_data['album']
  response = requests.get(
    url = 'https://api.spotify.com/v1/search?q='+query_string+'&type=track&market=ES&limit=10',
    headers = {
      'Authorization': 'Bearer ' + token
    }
  )

  text = response.text
  data = json.loads(text)

  loop = data['tracks']['total']
  if (data['tracks']['total'] > data['tracks']['limit']):
    loop = data['tracks']['limit']

  ids = []
  for i in range(0, loop):
    artists = []
    song_id = data['tracks']['items'][i]['id']
    song_name = data['tracks']['items'][i]['name']

    num_of_artists = len(data['tracks']['items'][i]['artists'])

    for j in range(0, num_of_artists):
      artists.append(data['tracks']['items'][i]['artists'][j]['name'])
    
    song_exists_already = Musicdata.objects.filter(id=song_id)

    if not song_exists_already:
      Musicdata.objects.create(
        id=song_id, 
        name=song_name,
        artists=artists
      )
    else:
      print('song already exists in db')

    ids.append({'id': song_id})

  return ids

@require_GET
def searchform_get(request):
    form = SearchForm()
    return render(request, 'recommender/searchform.html', {'form': form})

def index(request):
  return render(request, 'index.html')

def home(request):
  #if the user isn't authenticated, go back!
  if not request.user.is_authenticated: 
    return redirect('/best')

  return render(request, 'home.html')

def profile(request, user_id):
  #if the user isn't authenticated, go back!
  if not request.user.is_authenticated: 
    return redirect('/best')
  
  profile_data = getProfileData(request)
  
  return render(request, 'profile.html', {
    'photo': profile_data['photo'],
    'followers': profile_data['followers'],
    'last': getRecentlyPlayed(request)
  })

def topSongs(request, user_id):
  if not request.user.is_authenticated: 
    return redirect('/best')

  social = request.user.social_auth.get(provider='spotify')
  token = social.extra_data['access_token']

  try:
    response = requests.get(
      url = "	https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=10",
      headers = {
        'Authorization': 'Bearer ' + token
      },
    )
  except:
    print(response)

  text = response.text
  data = json.loads(text)

  song_list = []
  for song in data['items']:
   artist = song['artists'][0]['name']
   name = song['name']
   song_str = artist + ', ' + name
   song_list.append(song_str)
  
  profile_data = getProfileData(request)
  
  return render(request, 'profile.html', {
    'songs': song_list,
    'photo': profile_data['photo'],
    'followers': profile_data['followers'],
    'last': getRecentlyPlayed(request)
  })


def getProfileData(request):
  spotify_id = request.user.social_auth.get(provider='spotify').uid
  social = request.user.social_auth.get(provider='spotify')
  token = social.extra_data['access_token']
  
  response = requests.get(
    url = "https://api.spotify.com/v1/users/"+spotify_id, 
    headers = {
      'Authorization': 'Bearer ' + token
    }
  )
  text = response.text
  data = json.loads(text)

  photo = data['images'][0]['url']
  followers = data['followers']['total']
  return {
    'photo': photo,
    'followers': followers
  }

def getRecentlyPlayed(request):
  social = request.user.social_auth.get(provider='spotify')
  token = social.extra_data['access_token']

  response = requests.get(
    url = "	https://api.spotify.com/v1/me/player/recently-played?limit=1",
    headers = {
      'Authorization': 'Bearer ' + token
    }
  )

  text = response.text
  data = json.loads(text)

  last_played = data['items'][0]['track']['id']

  return last_played