# this file is to process the data from the users spotify
import os
from dotenv import load_dotenv
import time
from flask import url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# load the environment variables in
load_dotenv()


# function to create Spotify OAuth Object
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("client_ID"),
        client_secret=os.getenv("client_secret"),
        redirect_uri=url_for("views.redirect_page", _external=True),
        scope="user-library-read"
    )


# TODO: function to retrieve the user token from sessions
#   this is to be used in the homepage which prompts the user to login
def get_token():
    user_token = session.get("token_info", None)
    # if the token doesn't exist, redirect to the login page
    # TODO: should we redirect to views.redirect?
    if not user_token:
        redirect(url_for("views.redirect", _external=False))  # external = false makes it so the except catches the error

    # if the token is about to expire, refresh the token
    expire_time = user_token["expires_at"] - int(time.time())
    if expire_time < 120:
        oauth = create_spotify_oauth()
        user_token = oauth.refresh_access_token(user_token["refresh_token"])
    # return the refreshed token
    return user_token


# create data processing function to see how playable their music is at a party
# focus on danceability, bpm and valence
def playlist_performance(sp):
    # use the spotify object to access the playlist the user chose
    playlist = session["playlist"]
    # get all the songs/items in the playlist
    songs = sp.playlist_items(playlist_id=playlist["id"])["items"]
    # sum the valences, bpms, and danceability scores of tracks with for loop
    total_danceability = 0
    total_valence = 0
    total_bpm = 0
    total_popularity = 0
    total_energy = 0
    num_songs_processed = 0
    for song in songs:
        # first assess popularity
        total_popularity += song["track"]["popularity"]
        # create the object that creates the audio features and add to totals
        attributes = sp.audio_features(song["track"]["uri"])[0]
        total_danceability += attributes["danceability"]
        total_valence += attributes["valence"]
        total_energy += attributes["energy"]
        total_bpm += attributes["tempo"]
        num_songs_processed += 1

    # weighted average out all the statistics (prioritize danceability, popularity, and energy
    party_score_dec = (0.25 * total_danceability + 0.25 * total_popularity +
                   0.25 * total_energy + 0.15 * total_valence) / num_songs_processed;
    average_bpm = total_bpm / num_songs_processed;
    if(average_bpm > 140 or average_bpm < 110):
        party_score_dec += 0.05
    else:
        party_score_dec += 0.1

    party_score = party_score_dec
    return party_score


def music_blurb(percentage):
    # TODO: create a dictionary with four playability levels as keys and a messages list as values
    #   using the random.choice() function from the random library, randomly pull a message string
    #   and return the blurb
    blurb = ""
    if percentage < 25:
        blurb = "They'll love your music!"
    elif percentage >= 25 and percentage < 50:
        blurb = "Maybe delete those Kid Cudi songs..."
    elif percentage >= 50 and percentage < 75:
        blurb = "Who put this guy on aux?"
    elif percentage >= 75:
        blurb = "Damn is everything okay?"
    return blurb

# TODO: create a function that uses the recommendations() function in the spotipy library to generate recommendations

