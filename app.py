#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response,  flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
#from flask_wtf import FlaskForm (not used here but in forms.py)
from datetime import datetime
from flask_migrate import Migrate

from forms import *
import re
from operator import itemgetter # for sorting lists if tuples

from models import Genre, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app =  Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db.init_app(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)  


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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


  # Get data on the venues and populate the data list.  Grouped by City
  # venues = Venue.query.order_by(Venue.state, Venue.city.asc()).all()
  # Order_by here not working since order changes is lost when we put it into a set.
  venues = Venue.query.all()
  
  data = []  # A list of dictionaries, where city, state, and venues are dictionary keys
  
  # Create a set of all the cities/states combinations uniquely
  cities_states = set()
  for Venue in venues:
    cities_states.add([(Venue.city, Venue.state)]) # this line adds tuple


  #Turning the state into an orderd list
  cities_states = list(cities_states) 
  cities_states.sort(key=itemgetter(1,0)) # sorts the second column first (state) then by city

  now = datetime.now()

  # iterating over the unique values to seed the data dictionary with city/state locations
  for loc in cities_states:
    venues_list =  []

    for venue in venues:
      if(venue.city == loc[0] and venue.state == loc[1]):
          # If we've got a venue to add, check how many upcoming shows it has
          venue_shows = Show.query.filter_by(venue_id=venue.id).all()
          num_upcoming = 0
          for show in venue_shows:
            if show.start_time > now:
              num_upcoming += 1

          venues_list.append({
            "id", venue.id,
            "name", venue.name,
            "num_upcoming_shows", num_upcoming,
          })

    # After all venues are added to the list for a given location, add it to the data dictionary
    data.append({
      "city": loc[0],
      "state": loc[1],
      "venues": venues_list
    })

    #TODO: Add dummy data below to database 

    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term = request.form.get('search_term', '').strip()

  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all() #wildcard search before and after

  venue_list = []
  now = datetime.now()
  for venue in venues:
    venue_shows = Show.query.filter_by(venue_id=venue.id).all()
    num_upcoming = 0
    for show in venue_shows:
      if show.start_time > now:
        num_upcoming += 1

    venue_list.append({
      "id", venue.id,
      "name", venue.name,
      "num_upcoming_shows", num_upcoming
    })
  
  response = {
    "Count": len(venues),
    "data": venue_list,
  }

  ##response dummy data
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)
  

###################

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id): # shows the venue page with the given venue_id
  # Get all the data from the DB and populate the data dictionary (context)

  venue = Venue.query.get(venue_id)
  print(venue)

  if not venue:
    # Didn't return a value or user must've hand-typed a link into the browser that doesn't exist
    # Redirect home
    return redirect(url_for('index'))
  else:
    # genres need to be a list of genre strings for the template format required
    genres = [genre.name for genre in venue.genres]

    # get a list of shows, and count the ones in the past and future
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()

    for show in venue.shows:
      if show.start_time > now:
        upcoming_shows_count += 1
        upcoming_shows.append({
          "artsist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        })
      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
          "artsist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        })

    ##data template
    data = {
      "id": venue_id,
      "name": venue.name,
      "genres": genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      # add the dashes for the phone number
      "phone": (venue.phone[:3] + '-'  + venue.phone[3:6] + '-' + venue.phone[6:]),
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows": upcoming_shows,
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
  form = VenueForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  address = form.address.data.strip()
  phone = form.phone.data

  # normalizing the DB using strip() to remove anything from phone that isn't a number
  phone = re.sub('\D', '', phone) #eg (819)392-1658 -->  8193921658
  genres = form.genres.data
  seeking_talent  = True if form.seeking_talent.data == 'yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()

  #redirect user back to form if error occur in form validation
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_venue_submission'))
  
  else:
    error_in_insert = False

    #insert form data into DB
    try:
      #creates new venue with all fields except genres
      new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, \
        seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
        website=website, facebook_link=facebook_link)
      # genres cant take a list of strings, it needs to be assigned to db objects
      # genres forom the form is like : ['Alternative', 'Classical', 'Country']

      for genre in genres:        
        fetch_genre = db.session.query(Genre).filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
        #fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
        if fetch_genre:
          #if found genre append it to the list
          new_venue.genres.append(fetch_genre)

        else:
          #fetch_genre was None, it wasnt created yet, therefore we create it
          new_genre = Genre(name=genre)
          db.session.add(new_genre)
          new_venue.genres.append(new_genre) # created new genre and added it to the list
        
      db.session.add(new_venue)
      db.session.commit()
    
    except Exception as e:
      error_in_insert = True
      print(f'Exception "{e}" in create_venue_submission()')
      db.session.rollback()
    finally:
      db.session.close()

    if not error_in_insert:
      # on succesful db insert, flash success
      flash('Venue' + request.form['name'] + 'was succesfully listed')
      return redirect(url_for('index'))

    else:
      flash('An error occured. Venue' + name + 'could not be listed')
      print('Error in create_venue_submission()')
      #return redirect(url_for('create_venue_submission()'))
      abort(500)


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  #DELETEs venue based on AJX call from venue page
  venue = Venue.query.get(venue_id)
  if not venue:
    # where the user somehow faked this call, redirect them to the homepage
    return redirect(url_for('index'))
  else:
    error_on_delete = False
    # need to hang on venue name since it will lost after delete
    venue_name = venue.name
    try:
      db.session.delete(venue)
      db.session.commit()
    except:
      error_on_delete = True
      db.session.rollback()
    finally:
      db.session.close()
    
    if error_on_delete:
      flash(f'An error occured deleting venue {venue_name}')
      print('Error in delete_venue()')
      abort(500)
    else:
      #flash('succesfully removed venue (venue_name)')
      # return redirect(url_for('venues))
      return jsonify({
        'deleted': True,
        'url': url_for('venues')
      })



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.order_by(Artist.name).all()  #sorts input alphabetically

  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
    
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get("search_term", "").strip()

  #use filter, not filter_by when doing LIKE search
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all() #wildcard seach before and after

  artist_list = []
  now = datetime.now()

  for artist in artists:
    artist_shows = Show.query.filter_by(artist_id=artist.id).all()
    num_upcoming = 0
    for show in artist_shows:
      if show.start_time > now:
        num_upcoming += 1
      
    artist_list.append({
      "id":artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming #FYI, Template does nothing with this
    })


    response = {
      "count": len(artists),
      "data": artist_list
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # displays the artist page with the given artist_id

  # Get all the data from the DB and populate the data dictionary (context)
  artist = Artist.query.get(artist_id)
  print(artist)
  if not artist:
    # Didn't return one, user must've hand-typed a link into the browser that doesn't exist
    # Redirect Home
    return redirect(url_for('index'))
  
  else:
    #genres need to be a list of genre strings for the template
    genres = [genre.name for genre in artist.genres]

    # get a list of shows and count the ones in the past and future
    past_shows = []
    past_show_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()
    for show in artist.shows:
      if show.start_time > now:
        upcoming_show_count += 1
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.id,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
        })
      
      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
        })


    data = {
      "id": artist_id,  
      "name": artist.name,
      "genres": genres,
      # "address": artist.address,
      "city": artist.city,
      "state": artist.state,
      # Put the dashes back into phone number
      "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": upcoming_shows_count
    }

    # data = list(filter(lambda d: d['id'] ==
    #                    artist_id, [data1, data2, data3]))[0]

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # get existing data from the DB
  artist = Artist.query.get(artist_id)
  if not artist:
    # when user enters a URL that doesnt exist, redirect them to the homepage
    return redirect(url_for('index'))
  else:
    # Otherwise, valid artist.  We can prepopulate the form with existing data like this.
    # Prepopulate the form with the current values.  This is only used by template rendering!
    form = ArtistForm(obj=artist)

    # genres need to be a list of genre strings for the template
    genres = [ genre.name for genre in artist.genre]

    artist = {
      "id": artist_id,
      "name": artist.name,
      "genres": genres,
      # "address": artist.address,
      "city": artist.city,
      "state": artist.state,
      # Put the dashes back into phone number
      "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }


    ## dummy data to populate db iniitally
    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }

    return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm() #code similar to edit_venue_submission()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data

  #address = form.address.data.strip()
  phone = form.phone.data.strip()
  # Normalize DB.  Strip anything from phone that isn't a number
  phone = re.sub('\D', '', phone) # e.g. (819) 392-1234 --> 8193921234

  genres = form.genres.data
  seeking_venue = True if form.seeking_venue.data == 'Yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()

  # Redirect back to form if errors in form validation
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))
  
  else:
    error_in_update = False

    # insert form data into DB
    try:
      #first get existing artist object
      artist = Artist.query.get(artist_id)

      #update the fields
      artist.name = name
      artist.city = city
      artist.state = state
      #artist.address = address
      artist.phone = phone

      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
      artist.image_link = image_link
      artist.website = website
      artist.facebook_link = facebook_link


      # First we need to clear (delete) all the existing genres off the artist otherwise it just adds them
      
      # For some reason this didn't work! Probably has to do with flushing/lazy, etc.
      # for genre in artist.genres:
      #     artist.genres.remove(genre)
                  
      # artist.genres.clear()  # Either of these work.
      artist.genres = []
      
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):


  print(venue_id)
  form = VenueForm(request.form)
  print('In sub form')
  if form.validate():
    try:
      venue_details = Venue.query.get(venue_id)
      
      venue_details.name = form.name.data,
      venue_details.genres = "".join(form.genres.data),
      venue_details.state = form.state.data,
      venue_details.address = form.address.data,
      venue_details.city = form.city.data,
      venue_details.phone = form.phone.data,
      venue_details.website_link = form.website_link.data,
      venue_details.facebook_link = form.facebook_link.data,
      venue_details.seeking_description = form.facebook_link.data,
      venue_details.image_link = form.image_link.data,
      venue_details.seeking_talent = form.seeking_talent.data,

      db.session.commit()
      flash('Venue' + request.form['name'] + 'was succesfully listed')

    except:
      print('code displays when `except` possibility occurs')
      print(sys.exc_info())
      flash('venue' + request.form['name'] + 'Failure to update')
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

  form = ArtistForm(request.form)

  if form.validate():
    try:
      new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = "".join(form.genres.data),
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data,
        website_link = form.website_link.data
      )
      
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + 'was succesfully listed')
  
    except:
      print(sys.exc_info())
      flash('Artist ' + request.form['name'] + 'Failure, It was not  listed succesfully')
      db.session.rollback()
    finally:
      db.session.close()
      return render_template('pages/home.html')
  else:
    flash('Could not create artist, Kindly enter a valid input')


### Delete Artist
@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
  try:
    artist =  Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Successfully deleted!!!')
  except:
    db.session.rollback()
    flash('Failed to delete')
  finally:
    db.session.close()
    return redirect(url_for('index'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []
  result = Show.query.all()

  for item in result:
    artist  = Artist.query.get(item.artist_id)
    venue = Venue.query.get(item.venue_id)
    item_obj = {
      "venue_id":  venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": item.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    data.append(item_obj)

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():


  form = ShowForm(request.form)
  if form.validate():
    try:
      show_new = Show(artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data)
      db.session.add(show_new)
      db.session.commit()
      flash("Show was successfully listed!!")

    except:
      print(sys.exc_info())
      flash('Failled to list the shows') ## <--eresponsible for showing error messages
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

#if __name__ == '__main__':
#    port = int(os.environ.get('PORT', 4000))
#    app.run(host='0.0.0.0', port=port)
