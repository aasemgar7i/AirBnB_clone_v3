#!/usr/bin/python3
""" places file """
from flask import jsonify, request, abort
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.amenity import Amenity
from models.state import State
import json


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_all_places(city_id):
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    data = json.loads(request.data)
    if not data:
        abort(400, description="Not a JSON")
    if 'user_id' not in data:
        abort(400, description="Missing user_id")
    user_id = data['user_id']
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    if 'name' not in data:
        abort(400, description="Missing name")
    data['city_id'] = city_id
    place = Place(**data)
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    data = json.loads(request.data)
    if not data:
        abort(400, description="Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def search_places():
    try:
        data = json.loads(request.data)
    except Exception:
        return jsonify({"error": "Not a JSON"}), 400

    if not data or all(not data.get(key) for key in data.keys()):
        places = storage.all(Place).values()
        return jsonify([place.to_dict() for place in places])

    places = set()

    states = data.get("states", [])
    for state_id in states:
        state = storage.get(State, state_id)
        if state:
            places.update(state.places)

    cities = data.get("cities", [])
    for city_id in cities:
        city = storage.get(City, city_id)
        if city:
            places.update(city.places)

    for state_id in states:
        state = storage.get(State, state_id)
        if state:
            for city in state.cities:
                places.update(city.places)

    for city_id in cities:
        city = storage.get(City, city_id)
        if city:
            places.update(city.places)

    amenities = data.get("amenities", [])
    for amenity_id in amenities:
        amenity = storage.get(Amenity, amenity_id)
        if amenity:
            places = {place for place in places if amenity in place.amenities}

    return jsonify([place.to_dict() for place in places])
