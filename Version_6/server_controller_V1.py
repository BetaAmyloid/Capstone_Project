from flask import Flask, render_template
from flask_socketio import SocketIO
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins for testing

@app.route('/')
def index():
    return render_template('web_controller_V1.html')

#------------------------------------------------------------------
# Response
#                                        3      0    1    2         0      1      2               N seconds
# PrintStringArr();     //Serial Input: <ID> <Left, Mid, Right> <Forward, Stop, Backward> <Interval of motor working>

@socketio.on('data_sent')
def handle_button1(data):
    print(f"Received: {data}")
    vertical_data = data.get('vertical', 1)
    horizontal_data = data.get('horizontal', 1)

    # Reading from JSON
    with open("/home/buslon/Desktop/CoffeeBeanProgram/ImageDetection/Version_6/JSON/controller_V1.json", "r") as file:
        json_data = json.load(file)

    # Modify the data (example)
    json_data["vertical"] = vertical_data
    json_data["horizontal"] = horizontal_data

    # Write back to JSON
    with open("/home/buslon/Desktop/CoffeeBeanProgram/ImageDetection/Version_6/JSON/controller_V1.json", "w") as file:
        json.dump(json_data, file, indent=4)

    response = f"Server received vertical: {vertical_data}, horizontal: {horizontal_data}"
    socketio.emit('data_received', response)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
