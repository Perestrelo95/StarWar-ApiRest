"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet
import requests
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# class Starwars:
#     all_starwars = []

#     def __init__(self, content):
#         self.id = len(self.__class__.all_starwars) + 1
#         self.content = content
#         self.date = datetime.utcnow
#         self.__class__.all_starwars.append(self)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "content": self.content,
#         }

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def list_user():
    users = User.query.all()
    user_map = list(map(
        lambda user: user.serialize(),
        users
    ))
    return jsonify(user_map), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def user_unique(user_id):
    user = User.query.filter_by(id=character_id).one_or_none()  
    
    return jsonify(user.serialize()), 200

@app.route('/characters', methods=['GET'])
def list_character():
    charracters = Character.query.all()
    charracters_map = list(map(
        lambda character: character.serialize(),
        charracters
    ))
    return jsonify(charracters_map), 200


@app.route('/characters/<int:character_id>', methods=['GET'])
def character_unique(character_id):
    character = Character.query.filter_by(id=character_id).one_or_none()  
    
    return jsonify(character.serialize()), 200


@app.route('/planets', methods=['GET'])
def list_planet():
    planets = Planet.query.all()
    planets_map = list(map(
        lambda planet: planet.serialize(),
        planets
    ))
    return jsonify(planets_map), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def planet_unique(planet_id):
    planet = Planet.query.filter_by(id=planet_id).one_or_none()  
    
    return jsonify(planet.serialize()), 200

@app.route('/favorites', methods=['GET'])
def favorites():
    favorites1 = FavoriteCharacter.query.all()
    favorites2 = FavoritePlanet.query.all()
    favorites2_map = list(map(
        lambda favorite2: favorite2.serialize(),
        favorites2
    ))
    favorites1_map = list(map(
        lambda favorite1: favorite1.serialize(),
        favorites1
    ))
    favorites_map = favorites1_map + favorites2_map

    return jsonify(favorites_map), 200

@app.route('/favorites/planets', methods=['GET', 'POST'])
def favorite_planet():
    if request.method == "GET":
        favorites_planet = FavoritePlanet.query.all()
        favorites_panets_map = list(map(
            lambda favorite: favorite.serialize(),
            favorites_planet
        ))
        return jsonify(favorites_panets_map), 200
    else:
        body = request.json
        favorite = FavoritePlanet(
            user_id = body["user_id"] if "user_id" in body else None, 
            planet_id = body["planet_id"] if "planet_id" in body else None
        )
        db.session.add(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 201


@app.route('/favorites/characters', methods=['GET', 'POST'])
def favorite_character():
    if request.method == "GET":
        favorites_character = FavoriteCharacter.query.all()
        favorites_characters_map = list(map(
            lambda favorite: favorite.serialize(),
            favorites_character
        ))
        return jsonify(favorites_characters_map), 200
    else:
        body = request.json
        favorite = FavoriteCharacter(
            user_id = body["user_id"] if "user_id" in body else None, 
            character_id = body["character_id"] if "character_id" in body else None
        )
        db.session.add(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 201
    

@app.route('/favorites/characters/<int:favoritecharacter_id>', methods=['GET', 'DELETE'])
def favoriteCharacter(favoritecharacter_id):
    favorites_character = FavoriteCharacter.query.filter_by(id=favoritecharacter_id).one_or_none() 
    if request.method == "GET":
        return jsonify(favorites_character.serialize()), 200
    else:
        deleted = favorites_character.delete()
        if deleted == False: return jsonify("algo salio mal"), 500 
        return "", 204

@app.route('/favorites/planets/<int:favoriteplanet_id>', methods=['GET', 'DELETE'])
def favoritePlanet(favoriteplanet_id):
    favorites_planet = FavoritePlanet.query.filter_by(id=favoriteplanet_id).one_or_none() 
    if request.method == "GET":
        return jsonify(favorites_planet.serialize()), 200
    else:
        deleted = favorites_planet.delete()
        if deleted == False: return jsonify("algo salio mal"), 500 
        return "", 204

@app.route('/llenarbd', methods=['POST'])
def llenarbd():
    r_body = request.json
    response = requests.get(f"https://www.swapi.tech/api/people?page=1&limit={r_body['limit']}")
    body = response.json()
    characters = body['results']
    new=0
    for character in characters:
        exist = Character.query.filter_by(name=character['name']).one_or_none()
        if exist: continue
        _response = requests.get(f"https://www.swapi.tech/api/people/{character['uid']}")
        _body = _response.json()
        properties = _body['result']['properties']
        _character = Character(
            name= properties["name"],
            birth_year= properties["birth_year"], 
            films= None, 
            gender = properties["gender"], 
            eye_color= properties["eye_color"]
        )
        new+=1
        db.session.add(_character)
    try:
        db.session.commit()
        return jsonify(f"added {new} characters"),200
    except Exception as error:
        db.session.rollback()
        return jsonify(f"{error.args}"), 400

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)