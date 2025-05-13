from flask import Flask, request, jsonify
import logging
from control_center import ControlCenter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
control_center = ControlCenter

@app.route('/messages', methods=['POST'])
def receive_message():
    """
    Handles POST requests to the /messages endpoint.
    It expects JSON data in the request body, extracts it,
    prints the data to the console, and returns a success response.
    """
    logging.info("Received request at /messages endpoint.")

    # Check if the request contains JSON data
    if not request.is_json:
        logging.warning("Request did not contain JSON data.")
        return jsonify({"error": "Request must be JSON"}), 400 # Bad Request

    # Get the JSON data from the request
    try:
        data = request.get_json()
        logging.info(f"Received JSON data: {data}")

        # You can customize this part based on the expected structure
        # For example, if you expect a 'message' field:
        # message_content = data.get('message', 'No message field found')
        # print(f"Message content: {message_content}")

        # For now, we'll just print the entire received JSON data
        print("--- Received Message Data ---")
        control_center.process_incoming_message(data)
        print("-----------------------------")

        # Return a success response
        return jsonify({"status": "success", "message_received": data}), 200 # OK

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": "An internal error occurred"}), 500 # Internal Server Error

# Main execution block
if __name__ == '__main__':
    # Run the Flask development server
    # host='0.0.0.0' makes the server accessible from any network interface
    # port=8088 specifies the port number
    # debug=True enables debug mode (useful for development, provides auto-reload and detailed errors)
    # Use debug=False in a production environment
    logging.info("Starting Flask server on port 8088...")
    # Use use_reloader=False to prevent the script from running twice in debug mode if not needed
    app.run(host='0.0.0.0', port=8088, debug=True, use_reloader=False)
    logging.info("Flask server stopped.")
