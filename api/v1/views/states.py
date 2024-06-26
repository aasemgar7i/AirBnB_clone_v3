#!/usr/bin/python3
"""state file"""
from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from api.v1.views import app_views
from models import storage
from models.state import State
import json


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_states():
    states = storage.all(State).values()
    if not states:
        abort(404)
    return jsonify([state.to_dict() for state in states])


@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
def get_state(state_id):
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route('/states/<state_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_state(state_id):
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    storage.delete(state)
    storage.save()
    return jsonify({}), 200


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    try:
        data = json.loads(request.data)
    except Exception as e:
        print("Exception during JSON parsing:", e)
        abort(400, description="Invalid JSON")

    if not data:
        abort(400, description="No JSON provided")
    if 'name' not in data:
        abort(400, description="Missing name")

    new_state = State(**data)
    storage.new(new_state)
    storage.save()
    return jsonify(new_state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    try:
        data = json.loads(request.data)
        print("Received JSON data:", data)
    except Exception as e:
        print("Exception during JSON parsing:", e)
        abort(400, description="Invalid JSON")

    if not data:
        abort(400, description="No JSON provided")
    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(state, key, value)
    state.save()
    return jsonify(state.to_dict()), 200
