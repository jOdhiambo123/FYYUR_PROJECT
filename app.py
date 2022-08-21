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
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

from jinja2 import Markup

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://oj:ottyjei@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('venue', lazy=True))

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('artist', lazy=True))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time=db.Column(db.DateTime , nullable=False)

def toList(string):
    result=string.split(',')
    return result

def toString(lst):
    result=','.join(lst)
    return result

def switch2bool(input):
    if input==None:
      return False
    else:
      return True

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
    # instead of just date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
# def format_datetime(value, format='medium'):
#   date = dateutil.parser.parse(value)
#   if format == 'full':
#       format="EEEE MMMM, d, y 'at' h:mma"
#   elif format == 'medium':
#       format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]

  locations=db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for location in locations:
    venue_list=[]
    entries={}
    venues=db.session.query(Venue).filter((Venue.state==location.state) & (Venue.city==location.city)).all()
    for venue in venues:
      venue_data={}
      venue_data["id"]=venue.id
      venue_data["name"]=venue.name
      venue_data["num_upcoming_shows"]=len(venue.shows)
      venue_list.append(venue_data)
    entries["city"]=location.city
    entries["state"]=location.state
    entries["venues"]=venue_list
    data.append(entries)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term= request.form.get('search_term', '')
  results=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  count=len(results)
  data=[]
  for result in results:
    response_data={}
    response_data['id']=result.id
    response_data['name']=result.name
    response_data['num_upcoming_shows']=len(result.shows)
    data.append(response_data)


  response={
    "count":count ,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.filter_by(id=venue_id).one()
  past_shows=[]
  upcoming_shows=[]
  for show in venue.shows:
    past_shows_data={}
    upcoming_shows_data={}
    today=datetime.today()
    if show.start_time<today:
      past_shows_data["artist_id"]=(show.artist).id
      past_shows_data["artist_name"]=(show.artist).name
      past_shows_data["artist_image_link"]=(show.artist).image_link
      past_shows_data["start_time"]=show.start_time
      past_shows.append(past_shows_data)
    else:
      upcoming_shows_data["artist_id"]=(show.artist).id
      upcoming_shows_data["artist_name"]=(show.artist).name
      upcoming_shows_data["artist_image_link"]=(show.artist).image_link
      upcoming_shows_data["start_time"]=show.start_time
      upcoming_shows.append(upcoming_shows_data)



  data={
    "id": venue.id,
    "name": venue.name,
    "genres": toList(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent":venue.seeking_talent ,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    venue=Venue(name=request.form["name"],city = request.form["city"],state = request.form["state"],phone = request.form["phone"],
    address= request.form["address"],facebook_link = request.form["facebook_link"],genres = toString(request.form.getlist("genres")),
    website_link = request.form["website_link"],image_link = request.form["image_link"],seeking_talent =switch2bool(request.form.get("seeking_talent")),
     seeking_description = request.form["seeking_description"])
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success

    flash('Venue ,' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue=Venue.query.filter_by(id=venue_id).one()
    db.session.delete(venue)
    db.session.commit()
    flash("venue successfully deleted!")
  except:
    db.session.rollback()
    flash("an error occured during deletion, Try again")
  finally:
    db.session.close()
    return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term= request.form.get('search_term', '')
  results=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count=len(results)
  data=[]
  for result in results:
    response_data={}
    response_data['id']=result.id
    response_data['name']=result.name
    response_data['num_upcoming_shows']=len(result.shows)
    data.append(response_data)


  response={
    "count":count ,
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist=Artist.query.filter_by(id=artist_id).one()
  past_shows=[]
  upcoming_shows=[]
  for show in artist.shows:
    past_shows_data={}
    upcoming_shows_data={}
    today=datetime.today()
    if show.start_time<today:
      past_shows_data["venue_id"]=(show.venue).id
      past_shows_data["venue_name"]=(show.venue).name
      past_shows_data["venue_image_link"]=(show.venue).image_link
      past_shows_data["start_time"]=show.start_time
      past_shows.append(past_shows_data)
    else:
      upcoming_shows_data["venue_id"]=(show.venue).id
      upcoming_shows_data["venue_name"]=(show.venue).name
      upcoming_shows_data["venue_image_link"]=(show.venue).image_link
      upcoming_shows_data["start_time"]=show.start_time
      upcoming_shows.append(upcoming_shows_data)



  data={
    "id": artist.id,
    "name": artist.name,
    "genres": toList(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue":artist.seeking_venue ,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
   }

  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.filter_by(id=artist_id).one()

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist=Artist.query.filter_by(id=artist_id).one()
    artist.name=request.form["name"]
    artist.city = request.form["city"]
    artist.state = request.form["state"]
    artist.phone = request.form["phone"]
    artist.facebook_link = request.form["facebook_link"]
    artist.genres = toString(request.form.getlist("genres"))
    artist.website_link = request.form["website_link"]
    artist.image_link = request.form["image_link"]
    artist.seeking_venue = switch2bool(request.form.get("seeking_venue"))
    artist.seeking_description = request.form["seeking_description"]
    db.session.add(artist)
    db.session.commit()
    flash("Artist updated successfully")
  except:
    db.session.rollback()
    flash("artist update failed, try again")
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.filter_by(id=venue_id).one()

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    venue=Venue.query.filter_by(id=venue_id).one()
    venue.name=request.form["name"]
    venue.city = request.form["city"]
    venue.state = request.form["state"]
    venue.phone = request.form["phone"]
    venue.address= request.form["address"]
    venue.facebook_link = request.form["facebook_link"]
    venue.genres = toString(request.form.getlist("genres"))
    venue.website_link = request.form["website_link"]
    venue.image_link = request.form["image_link"]
    venue.seeking_talent = switch2bool(request.form.get("seeking_venue"))
    venue.seeking_description = request.form["seeking_description"]
    db.session.add(venue)
    db.session.commit()
    flash("venue updated successfully!")
  except:
    db.session.rollback()
    flash("venue update failed, try again")
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist=Artist(name=request.form["name"],city = request.form["city"],state = request.form["state"],phone = request.form["phone"],
    facebook_link=request.form["facebook_link"],genres=toString(request.form.getlist("genres")),website_link=request.form["website_link"],
    image_link=request.form["image_link"],seeking_venue=switch2bool(request.form.get("seeking_venue")),seeking_description=request.form["seeking_description"] )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ,' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  shows=Show.query.all()
  for show in shows:
    show_details={}
    show_details["venue_id"]=show.venue_id
    show_details["venue_name"]=(show.venue).name
    show_details["artist_id"]=show.artist_id
    show_details["artist_name"]=(show.artist).name
    show_details["artist_image_link"]=(show.artist).image_link
    show_details["start_time"]=show.start_time
    data.append(show_details)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show=Show(artist_id=int(request.form["artist_id"]) ,venue_id=int(request.form["venue_id"]),start_time=request.form["start_time"] )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


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
    app.run(host='0.0.0.0')

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''


