# this is for establishing the blueprint of the routes that don't have to do with login
from flask import Blueprint, render_template, request, session, redirect
# import local files here
from Website.spotify_dp import *
# TODO: see why the html files cannot be found
views = Blueprint("views", __name__)


# home route: this will just have a html/css template with a button that redirects them to the login
@views.route("/")
def homepage():
    # TODO: create the homepage using html/css
    #   should have a login button that redirects to the login page
    #   --> have to set up a redirect route?
    return render_template("homepage.html")


# TODO create a login route that redirects to the spotify OAuth Page
@views.route("/login")
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)


# TODO create a redirect route that handles the redirect uri once the user has been authenticated
@views.route("/redirect")
def redirect_page():
    # clear the session
    session.clear()
    # get the auth code from the request
    auth_code = request.args.get('code')
    # get an auth token using OAuth
    auth_token = create_spotify_oauth().get_access_token(auth_code)
    # store this token in the session
    session["token_info"] = auth_token
    # once the token is stored, redirect the users to the results page
    return redirect(url_for("views.getplaylist", _external=True))


# select playlist route
@views.route("/getplaylist", methods=["GET", "POST"])
def getplaylist():
    if request.method == "POST":
        # get the playlist name the user wants us to search for
        potential_name = request.form.get("playlist")
        # try-catch block for retrieving the token
        try:
            user_token = get_token()
        except:
            return redirect(url_for("views.redirect", _external=True))
        # create the spotify instance with the access token
        sp = spotipy.Spotify(auth=user_token["access_token"])
        # get the user playlists with Spotify instance
        user_playlists = sp.current_user_playlists()["items"]
        playlist_name = ""
        for playlist in user_playlists:
            if playlist["name"] == potential_name:
                # save playlist name in session
                playlist_name = playlist["name"]
                # name the playlist
                session["playlist"] = playlist
                # redirect to the results page
                return redirect(url_for("views.results", _external=True))
        # if we cannot find the playlist, redirect to the same page, but with the error message popped up
        if playlist_name == "":
            # TODO: see what's wrong with the notfound bool text not showing up
            redirect(url_for("views.getplaylist", notfound=True))
    return render_template("getplaylist.html", notfound=False)


# results route
@views.route("/results")
def results():
    # try-catch block for retrieving the token
    try:
        user_token = get_token()
    except:
        return redirect(url_for("views.redirect", _external=True))
    # create the spotify instance with the access token
    sp = spotipy.Spotify(auth=user_token["access_token"])

    # pass the initialized spotify instance into the data calculator function
    # will return a dictionary with keys popularity, danceability, energy, valence, and bpm
    # TODO: use the values from these keys to fill in variables in the render_template function
    playability = round(playlist_performance(sp), 2)
    # TODO: complete the music blurb function
    blurb = music_blurb(playability)
    return render_template("results.html", playlist_name=session["playlist"]["name"], percentage=playability, blurb=blurb)


# below this comment are routes that don't necessarily link to anything else
# build these out last bc these are a little unnecessary to the functioning of the website
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# about route
@views.route("/about")
def about():
    return render_template("about.html")


# privacy route
@views.route("/privacy")
def privacy():
    return render_template("privacy.html")


# contact route
@views.route("/contact")
def contact():
    return render_template("contact.html")
