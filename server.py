from flask import Flask, request, jsonify
import logging
from control_center import ControlCenter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
control_center = ControlCenter()  # Create an instance of ControlCenter

@app.route('/messages', methods=['POST'])
def receive_message():
    """
    Handles POST requests to the /messages endpoint.
    It expects JSON data in the request body, extracts it,
    prints the data to the console, and returns a success response.
    """
    # logging.info("Received request at /messages endpoint.")

    # Check if the request contains JSON data
    if not request.is_json:
        logging.error("Request did not contain JSON data.")
        return jsonify({"error": "Request must be JSON"}), 400 # Bad Request

    # Get the JSON data from the request
    try:
        data = request.get_json()
        control_center.process_incoming_message(data)

        # Return a success response
        return jsonify({"status": "success", "message_received": data}), 200 # OK

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": "An internal error occurred"}), 500 # Internal Server Error

# Endpoint to get all rockets in the fleet
@app.route('/rockets', methods=['GET'])
def get_all_rockets():
    """
    Handles GET requests to the /rockets endpoint.
    It returns a list of all rockets in the fleet.
    """
    logging.info("Received request at /rockets endpoint.")

    try:
        # Get the list of rockets from the control center
        rockets = control_center.list_rockets_in_fleet()

        # Return the list of rockets as JSON
        return jsonify(rockets), 200
    
    except Exception as e:
        logging.error(f"Error listing rockets: {e}")
        return jsonify({"error": "An internal error occurred"}), 500 # Internal Server Error

# Endpoint to get a specific rocket's information by ID
@app.route('/rockets/<rocket_id>', methods=['GET'])
def get_rocket(rocket_id):
    """
    Handles GET requests to the /rockets/<rocket_id> endpoint.
    It returns the details of a specific rocket by its ID.
    """
    logging.info(f"Received request at /rockets/{rocket_id} endpoint.")

    try:
        # Get the rocket details from the control center
        rocket = control_center.get_rocket_by_id(rocket_id)

        if rocket:
            # Return the rocket details as JSON
            return jsonify(rocket), 200
        else:
            return jsonify({"error": "Rocket not found"}), 404 # Not Found
    
    except Exception as e:
        logging.error(f"Error retrieving rocket: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Endpoint to get all missions
@app.route('/missions', methods=['GET'])
def get_all_missions():
    """
    Handles GET requests to the /missions endpoint.
    Returns a list of all unique missions across all rockets.
    """
    logging.info("Received request at /missions endpoint.")

    try:
        missions = control_center.list_missions()
        return jsonify({"missions": missions}), 200
    
    except Exception as e:
        logging.error(f"Error listing missions: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Endpoint to get rockets by mission
@app.route('/missions/<mission>', methods=['GET'])
def get_rockets_by_mission(mission):
    """
    Handles GET requests to the /missions/<mission> endpoint.
    Returns all rockets assigned to a specific mission.
    """
    logging.info(f"Received request at /missions/{mission} endpoint.")

    try:
        rockets = control_center.get_rockets_by_mission(mission)
        if rockets:
            return jsonify({"mission": mission, "rockets": rockets}), 200
        return jsonify({"error": f"No rockets found for mission: {mission}"}), 404
    
    except Exception as e:
        logging.error(f"Error retrieving rockets for mission {mission}: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
    
# Main execution block
if __name__ == '__main__':
    # Run the Flask development server
    logging.info("Starting Flask server on port 8088...")
    # Use use_reloader=False to prevent the script from running twice in debug mode if not needed
    app.run(host='0.0.0.0', port=8088, debug=True, use_reloader=False)
    logging.info("Flask server stopped.")
