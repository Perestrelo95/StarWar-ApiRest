from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
# Base = declarative_base()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(110), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites_planets = db.relationship("FavoritePlanet", back_populates="favorite_user")
    favorites_characters = db.relationship("FavoriteCharacter", back_populates="favorite_user")

    def __init__(self, email, password, is_active):
        self.email = email
        self.password = password
        self.is_active = is_active

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    birth_year = db.Column(db.String(40))
    films = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    favorites = db.relationship("FavoriteCharacter", back_populates="favorite_character")

    def __init__(self, name, birth_year, films, gender, eye_color):
        self.name = name
        self.birth_year = birth_year
        self.films = films
        self.gender = gender
        self.eye_color = eye_color

        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "films": self.films,
            "gender": self.gender,
            "eye_color": self.eye_color
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    climate = db.Column(db.String(100))
    diameter = db.Column(db.Integer)
    population = db.Column(db.Integer)
    terrain = db.Column(db.Integer)
    favorites = db.relationship("FavoritePlanet", back_populates="favorite_planet")

    def __init__(self,name,climate,diameter,population,terrain):
        self.name = name
        self.climate = climate
        self.diameter = diameter
        self.population = population
        self.terrain = terrain

        db.session.add(self)
        db.session.commit()


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "diameter": self.diameter,
            "population": self.population,
            "terrain": self.terrain
        }


class FavoritePlanet(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id', ondelete="CASCADE"))
    favorite_user = db.relationship("User", back_populates="favorites_planets")
    favorite_planet = db.relationship("Planet", back_populates="favorites")

    def __init__(self, user_id, planet_id):
        self.user_id = user_id
        self.planet_id = planet_id

        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
            return True
        except Exception as error:
            print(error.args)
            return False

    def serialize(self):
        return {
            "id": self.id ,
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }

    
class FavoriteCharacter(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('character.id', ondelete="CASCADE"))
    favorite_user = db.relationship("User", back_populates="favorites_characters")
    favorite_character = db.relationship("Character", back_populates="favorites")

    def __init__(self, user_id, character_id):
        self.user_id = user_id
        self.character_id = character_id

        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
            return True
        except Exception as error:
            print(error.args)
            return False

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }