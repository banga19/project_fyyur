from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genre = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    show = db.relationship("Show", backref="venues", lazy=False, cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Venue Id: {self.id}, Name: {self.name}, State: {self.state}>'



class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genre = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    shows = db.relationship("Show", backref="artists", lazy=False, cascade="all, delete-orphan")


    def __repr__(self):
      return f'<Artist ID: {self.id},  Name: {self.name}>'
    



class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True )
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    artist_name = db.Column(db.String(120), db.ForeignKey("artists.name"), nullable=True)
    artist_image_link = db.Column(db.String(200), db.ForeignKey("artists.image_link", nullable=True))

    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    venue_name = db.Column(db.String(120), db.ForeignKey("venues.name", nullable=False))
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Show id={self.id}, artist_id={self.artist_id}, venue_id={self.venue_id}, start_time={self.start_time}>"


