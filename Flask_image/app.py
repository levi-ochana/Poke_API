from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)

# Configure MongoDB connection (MongoDB running in a Docker container)
app.config["MONGO_URI"] = "mongodb://admin:secret_password@mongo:27017/pokemon_db?authSource=admin"  # Connect to MongoDB via Docker container name
mongo = PyMongo(app)

# Function to convert ObjectId to string and handle dict/list
def json_serializable(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):  # if the object is a dictionary
        return {key: json_serializable(value) for key, value in obj.items()}  # recursively convert each item
    elif isinstance(obj, list):  # if the object is a list
        return [json_serializable(item) for item in obj]  # recursively convert each item in the list
    return obj  # return as is for other types like string, int

# Endpoint to retrieve all Pokémon
@app.route("/api/pokemon", methods=["GET"])
def get_pokemon():
    try:
        pokemon_list = mongo.db.pokemon.find()  # Retrieve all Pokémon from the DB
        pokemon_list = [pokemon for pokemon in pokemon_list]
        # Convert ObjectId to string before returning the response
        return jsonify([json_serializable(pokemon) for pokemon in pokemon_list])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to add a new Pokémon
@app.route("/api/pokemon", methods=["POST"])
def add_pokemon():
    try:
        data = request.get_json()
        
        # Check if required data exists
        if not all(key in data for key in ["name", "type", "abilities"]):
            return jsonify({"error": "Missing required fields: name, type, abilities"}), 400

        pokemon = {
            "name": data["name"],
            "type": data["type"],
            "abilities": data["abilities"]
        }

        mongo.db.pokemon.insert_one(pokemon)  # Insert new Pokémon into the DB
        return jsonify({"message": "Pokémon saved to database."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to retrieve a Pokémon by name
@app.route("/api/pokemon/<name>", methods=["GET"])
def get_pokemon_by_name(name):
    try:
        pokemon = mongo.db.pokemon.find_one({"name": name})
        if pokemon:
            # Convert ObjectId to string before returning the response
            return jsonify(json_serializable(pokemon))
        else:
            return jsonify({"message": "Pokémon not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
