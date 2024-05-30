from flask import Flask, redirect, render_template, request, session, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'DH10'

global temperature
temperature = "N/A"
global message
message = "NULL"
messages = []
global cloud_led_state
cloud_led_state = 0
global message_valid
message_valid = 0

@app.route('/')
def main_page():
    print(cloud_led_state)
    if cloud_led_state == 1:
        session['cloud_led_state'] = 'ON'
    elif cloud_led_state == 0:
        session['cloud_led_state'] = 'OFF'
    message = session.pop('message', None)
    return render_template('index.html', title='Home', cloud_led_state=cloud_led_state, temperature=temperature, messages=messages, message=message)

@app.route("/get_temperature", methods=['GET'])
def get_temperature():
    global temperature
    return temperature

@app.route('/update_temperature', methods=['POST'])
def update_temperature():
    global temperature
    data = request.form['temperature']
    temperature = data
    return 'Temperature updated successfully'

@app.route('/get_led', methods=['GET'])
def get_led():
    global cloud_led_state
    return str(cloud_led_state)

@app.route('/post_led', methods=['POST'])
def led_control():
    global cloud_led_state
    action = request.form['action']
    if action == 'on':
        cloud_led_state = 1
    elif action == 'off':
        cloud_led_state = 0
    return redirect(url_for('main_page'))

@app.route('/get_message', methods=['GET'])
def get_message():
    global message, message_valid
    if message_valid == 1:
        message_valid = 0
        return message
    else:
        return "NULL"

@app.route('/send_messages', methods=['POST'])
def send_messages():
    global message, message_valid, cloud_led_state
    message = request.form['message']
    messages.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S, ")) + "Mesaj: " + message)
    if message == 'ledON':
        cloud_led_state = 1
    elif message == 'ledOFF':
        cloud_led_state = 0
    message_valid = 1
    return redirect(url_for('main_page'))

@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    messages.clear()
    return redirect(url_for('main_page'))