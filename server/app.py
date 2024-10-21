#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS  # Import CORS for cross-origin requests
from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize CORS to allow cross-origin requests
CORS(app)

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get(self):
        """Retrieve all plants."""
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        """Add a new plant."""
        data = request.get_json()

        # Validate incoming data
        if not data or 'name' not in data or 'image' not in data or 'price' not in data:
            return make_response(jsonify({"error": "Invalid data"}), 400)

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )
        db.session.add(new_plant)
        db.session.commit()

        return make_response(jsonify(new_plant.to_dict()), 201)

api.add_resource(Plants, '/plants')

@app.route('/plants/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def plant_by_id(id):
    """Retrieve, update, or delete a plant by ID."""
    plant = Plant.query.get(id)

    # Check if the plant exists
    if not plant:
        return make_response(jsonify({"error": "Plant not found"}), 404)

    if request.method == 'GET':
        return make_response(jsonify(plant.to_dict()), 200)

    if request.method == 'PATCH':
        # Log incoming request content type
        print(f"Received Content-Type: {request.content_type}")  
        
        # Ensure the request is JSON
        if request.content_type != 'application/json':
            return make_response(jsonify({"error": "Invalid content type"}), 400)

        data = request.get_json()

        # Log the parsed JSON data
        print(f"Parsed JSON data: {data}")

        if data is None:
            return make_response(jsonify({"error": "No JSON data provided"}), 400)

        if "is_in_stock" in data:
            plant.is_in_stock = data['is_in_stock']

        db.session.commit()

        return make_response(jsonify(plant.to_dict()), 200)

    if request.method == 'DELETE':
        db.session.delete(plant)
        db.session.commit()

        return make_response('', 204)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
