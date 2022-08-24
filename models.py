from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Genre(db.Model):
    __tablename__ = "Genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
##artist to genre (many2many) association table
artist_genre_table = db.Table('artist_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

# venue to genre (may2many) association table 
venue_genre_table = db.Table('venue_genre_table', 
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id', primary_key=True)),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', primary_key=True))
)



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    #linking the genre association table for the m2m relationship  
    genres = db.relationship("Genre", secondary=venue_genre_table, backref=db.backref('venues'))
    # secondary links this to the associative (m2m) table name
    #can reference venue.george with the above statement
    # backref creates an attribute on Venue objects so we can also reference like: genre.venues
    
    website = db.Column(db.String(120))
   
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200)) 
    
    # Venue is the parent (one-to-many) of a Show (Artist is also a foreign key, in def. of Show)
    # In the parent is where we put the db.relationship in SQLAlchemy
    shows = db.relationship("Show", backref="venue", lazy=True)


    def __repr__(self):
        return f"<Venue Id: {self.id}, Name: {self.name}>"



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # Here we link the associative table for the m2m relationship with genre
    genres = db.relationship('Genre', secondary=artist_genre_table, backref=db.backref('artists'))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    
    # Artist is the parent (one-to-many) of a Show (Venue is also a foreign key, in def. of Show)
    # In the parent is where we put the db.relationship in SQLAlchemy
    shows = db.relationship("Show", backref="artist", lazy=True)  # Can reference show.artist (as well as artist.shows)

    def __repr__(self):
      return f'<Artist ID: {self.id},  Name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Start time required field

    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)    # Foreign key is the tablename.pk
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f"<Show id:{self.id}, artist_id:{self.artist_id}, venue_id:{self.venue_id}, start_time:{self.start_time}>"


