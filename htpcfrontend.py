from flask import Flask, jsonify, render_template, request
import hashlib, json, jsonrpclib, urllib

app = Flask(__name__)

from settings import *
from noneditable import *
from tools import *

from applications import *
from recently_added import *
from sabnzbd import *
from trakt import *
from currently_playing import *

@app.route('/')
@requires_auth
def index():
    return render_template('index.html',
        modules = MODULES,
        show_currently_playing = SHOW_CURRENTLY_PLAYING,
        fanart_backgrounds = FANART_BACKGROUNDS,
        applications = APPLICATIONS,
    )

@app.route('/xhr/play_episode/<int:episode_id>')
@requires_auth
def xhr_play_episode(episode_id):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    xbmc.Playlist.Clear(playlistid=1)

    item = { 'episodeid': episode_id }
    xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/play_movie/<int:movie_id>')
@requires_auth
def xhr_play_movie(movie_id):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    xbmc.Playlist.Clear(playlistid=1)

    item = { 'movieid': movie_id }
    xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/controls/<command>')
@requires_auth
def xhr_controls(command):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)

    if command == 'play_pause':
        xbmc.Player.PlayPause(playerid=1)

    elif command == 'stop':
        xbmc.Player.Stop(playerid=1)

    return jsonify({ 'success': True })

@app.route('/xhr/library')
@requires_auth
def xhr_library():
    return render_library()

@app.route('/xhr/library/<item_type>')
@requires_auth
def xhr_library_root(item_type):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    library = []
    title = "Movies"

    if item_type == 'movies':
        sort = { 'method': 'label' }
        library = xbmc.VideoLibrary.GetMovies(sort=sort)

    if item_type == 'shows':
        title = "TV shows"
        library = xbmc.VideoLibrary.GetTVShows()

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>')
@requires_auth
def xhr_library_show(show):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    library = xbmc.VideoLibrary.GetSeasons(tvshowid=show, properties=['tvshowid', 'season', 'showtitle'])

    title = library['seasons'][0]['showtitle']

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>/<int:season>')
@requires_auth
def xhr_library_season(show, season):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)

    sort = { 'method': 'episode' }
    library = xbmc.VideoLibrary.GetEpisodes(tvshowid=show, season=season, sort=sort, properties=['tvshowid', 'season', 'showtitle', 'episode', 'plot'])

    episode = library['episodes'][0]
    title = '%s - Season %s' % (episode['showtitle'], episode['season'])

    return render_library(library, title)

def render_library(library=None, title="Media library"):
    return render_template('library.html',
        library = library,
        title = title,
    )

if __name__ == '__main__':
    app.run(debug=True)
