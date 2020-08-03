#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database [DONE]

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean , default=True)
    seeking_description = db.Column(db.String(500))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate [DONE]

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean , default=True)
    seeking_description = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate [DONE]

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. [DONE]
class Show(db.Model):
    __tabelname__ : 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer , db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer , db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime , nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helper Methods.
#----------------------------------------------------------------------------#
def upcoming(id):
    num_upcoming_shows = 0
    shows = Show.query.filter_by(venue_id = id).all()
    for show in shows:
        if(show.start_time > datetime.now()):
            num_upcoming_shows += 1
    return num_upcoming_shows
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data. [Done]
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # MOCK UP :
    # data=[{
    #   "city": "New York",
    #   "state": "NY",
    #   "venues": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }]
    data = []
    venues = Venue.query.all()
    venue_cities = set()
    for venue in venues:
        venue_cities.add((venue.city,venue.state))

    for a in venue_cities:
        data.append({"city":a[0],"state":a[1],"venues":[]})

    # get number of upcoming shows for each venue
    for venue in venues:
        num_upcoming_shows = upcoming(venue.id)

        # for each entry, add venues to matching city/state
        for entry in data:
            if(venue.city == entry['city'] and venue.state == entry['state']):
                entry['venues'].append({"id":venue.id, "name":venue.name,"num_upcoming_shows":num_upcoming_shows})

    return render_template('pages/venues.html', areas=data);



@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. [Done]
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # MOCK UP:
    # response={
    # "count": 1,
    # "data": [{
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "num_upcoming_shows": 0,
    # }]
    # }
    search_term = request.form.get('search_term', '')
    data = []
    counter = 0
    findings = Venue.query.filter(Venue.name.like(f'%{search_term}%')).all()
    for respone in findings:
        counter += 1
        data.append({"id": respone.id, "name": respone.name,
        "num_upcoming_shows": upcoming(respone.id)})

    response={ "count": counter, "data": data }


    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id [Done]

    venue_shows_data = Show.query.filter_by(venue_id = venue_id).all()
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    for show in venue_shows_data:
        if(show.start_time > datetime.now()):
            upcoming_shows.append({"artist_id":show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))})
            upcoming_shows_count += 1
        else:
            past_shows.append({"artist_id":show.artist_id,
            "artist_name":Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time":format_datetime(str(show.start_time))})
            past_shows_count +=1

    venue_data = Venue.query.get(venue_id)
    list_of_char = venue_data.genres
    genres = []
    genre = ""
    for x in list_of_char:
        if(x == ','):
            genres.append(genre)
        elif(x == '{'):
            continue
        else:
            genre += x
    data = {
        "id": venue_id,
        "name": venue_data.name,
        "genres": genres,
        "address": venue_data.address,
        "city": venue_data.city,
        "state": venue_data.state,
        "phone": venue_data.phone,
        "website": venue_data.website,
        "facebook_link": venue_data.facebook_link,
        "seeking_talent": venue_data.seeking_talent,
        "seeking_description": venue_data.seeking_description,
        "image_link": venue_data.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead [Done]
    try:
        # load data from user input on submit
        form = VenueForm()
        # id = form.id.data
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        genres =form.genres.data
        image_link = form.image_link.data
        website = form.website.data
        facebook_link = form.facebook_link.data
        seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        seeking_description = form.seeking_description.data


        # create new Venue from form data
        new_venue = Venue( name = name , city = city , state = state,
         address = address , phone = phone ,image_link = image_link,
         facebook_link = facebook_link , genres = genres ,
         seeking_talent = seeking_talent , seeking_description = seeking_description)

        # TODO: modify data to be the data object returned from db insertion [Done]
        # add new venue to session and commit to database
        db.session.add(new_venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database [Done]
    # MOCK UP :
    #  data=[{
    #    "id": 4,
    #    "name": "Guns N Petals",
    #  }]

    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({"id": artist.id,"name": artist.name})

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. [Done]
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # MOCK UP:
    # response={
    # "count": 1,
    # "data": [{
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "num_upcoming_shows": 0,
    # }]
    # }
    search_term = request.form.get('search_term', '')
    data = []
    counter = 0
    findings = Artist.query.filter(Artist.name.like(f'%{search_term}%')).all()
    for respone in findings:
        counter += 1
        data.append({"id": respone.id,"name": respone.name,
        "num_upcoming_shows": upcoming(respone.id)})

    response={ "count": counter, "data": data }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artists table, using artist_id [Done]
    artist_shows_data = Show.query.filter_by(artist_id = artist_id).all()
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    for show in artist_shows_data:
        if(show.start_time > datetime.now()):
            upcoming_shows.append({
              "venue_id": show.venue_id,
              "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
              "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
              "start_time": format_datetime(str(show.start_time))
            })
            upcoming_shows_count+=1
        else:
            past_shows.append({
              "venue_id": show.venue_id,
              "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
              "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
              "start_time": format_datetime(str(show.start_time))
            })
            past_shows_count+=1


    artist_data = Artist.query.get(artist_id)
    list_of_char = artist_data.genres
    genres = []
    genre = ""
    for x in list_of_char:
        if(x == ','):
            genres.append(genre)
        elif(x == '{'):
            continue
        else:
            genre += x
    data={
        "id": artist_id,
        "name": artist_data.name,
        "genres": genres,
        "city": artist_data.city,
        "state": artist_data.state,
        "phone": artist_data.phone,
        "website": artist_data.website,
        "facebook_link": artist_data.facebook_link,
        "seeking_venue": artist_data.seeking_venue,
        "seeking_description": artist_data.seeking_description,
        "image_link": artist_data.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
        }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    form = ArtistForm()
    artist_data = Artist.query.filter_by(id = artist_id).first()

    artist={
    "id": artist_id,
    "name": artist_data.name,
    "genres": artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": artist_data.website,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": artist_data.seeking_venue,
    "seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id> [Done]
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing [Done]
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        artist = Artist.query.filter_by(id = artist_id).first()
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres
        artist.image_link = form.image_link.data
        artist.website = form.website.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    veneu_data = Venue.query.filter_by(id = venue_id).first()

    venue={
    "id": venue_id,
    "name": veneu_data.name,
    "genres": veneu_data.genres,
    "address": veneu_data.address,
    "city": veneu_data.city,
    "state": veneu_data.state,
    "phone": veneu_data.phone,
    "website": veneu_data.website,
    "facebook_link": veneu_data.facebook_link,
    "seeking_talent": True if veneu_data.seeking_talent == 'Yes' else False,
    "seeking_description": veneu_data.seeking_description,
    "image_link": veneu_data.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id> [Done]
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing [Done]
    # venue record with ID <venue_id> using the new attributes
    try:
        form = VenueForm()
        venue = Venue.query.filter_by(id = venue_id).first()
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website = form.website.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead [Done]
    try:
        form = ArtistForm()
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        genres = form.genres.data
        image_link = form.image_link.data
        facebook_link = form.facebook_link.data
        website = form.website.data
        seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        seeking_description = form.seeking_description.data

        # create new Artist from form data
        new_artist = Artist( name = name , city = city , state = state ,
         phone = phone , genres = genres , image_link = image_link ,
         facebook_link = facebook_link , website = website ,
         seeking_venue = seeking_venue ,seeking_description = seeking_description)

        # TODO: modify data to be the data object returned from db insertion [Done]
        # add new artist to session and commit to database
        db.session.add(new_artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead. [Done]
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data. [Done]
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # MOCK UP :
    # data=[{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 5,
    #   "artist_name": "Matt Quevedo",
    #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "start_time": "2019-06-15T23:00:00.000Z"
    # }]

    data = []
    # get all shows in Shows table
    shows = Show.query.all()
    for show in shows:
        venue_id = show.venue_id
        venue_name = Venue.query.filter_by(id=show.venue_id).first().name
        artist_id = show.artist_id
        artist_name = Artist.query.filter_by(id=show.artist_id).first().name
        artist_image_link = Artist.query.filter_by(id=show.artist_id).first().image_link
        start_time = format_datetime(str(show.start_time))

        data.append({"venue_id": venue_id,
        "venue_name": venue_name,
        "artist_id": artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": start_time})
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead [Done]
    try:
        form = ShowForm()
        # id = form.id.data
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = request.form['start_time']

        # create new Show from form data
        new_show = Show(artist_id = artist_id , venue_id = venue_id , start_time = start_time)

        # add new artist to session and commit to database
        db.session.add(new_show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')


    except:
        # TODO: on unsuccessful db insert, flash an error instead. [Done]
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
        db.session.rollback()

    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
