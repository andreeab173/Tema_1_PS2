from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import serial
import requests
import time

global send_message
send_message = 0

local_url = "http://localhost:5000/"
azure_url = "https://gloriais.azurewebsites.net/"

COM_PORT = "COM3"
BAUD_RATE = 9600

ser = serial.Serial(COM_PORT, BAUD_RATE)

def send_notification():
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USERNAME = 'andreeabartic17@gmail.com'
    SMTP_PASSWORD = 'aavy ynwq mvre tnim'
    RECIPIENT_EMAIL = 'barticalex@yahoo.com'

    message = MIMEMultipart()
    message['From'] = SMTP_USERNAME
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = 'Alertă! Inundație detectată!'

    body = "A fost detectată o inundație la data și ora: " + time.strftime("%Y-%m-%d %H:%M:%S")
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = message.as_string()
        server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, text)
        server.quit()
        print("E-mail trimis cu succes!")
    except Exception as e:
        print("Eroare la trimiterea e-mailului:", e)

def check_cloud_led_state():
    try:
        response = requests.get("https://gloriais.azurewebsites.net/get_led")
        if response.status_code == 200:
            cloud_led_state = int(response.text)
            print("Led state from cloud: "+ str(cloud_led_state))
            return cloud_led_state
        else:
            print(f"Failed to get cloud LED state. Status code: {response.status_code}")
            return None
    except Exception as e:
        print("Error:", e)
        return None

def check_cloud_message():
    try:
        response = requests.get("https://gloriais.azurewebsites.net/get_message")
        if response.status_code == 200:
            message = response.text
            print("Message from cloud: "+ str(message))
            return message
        else:
            print(f"Failed to get cloud message. Status code: {response.status_code}")
            return None
    except Exception as e:
        print("Error:", e)
        return None

def read_serial_and_send_data():
    global send_message, cloud_led_state
    last_message = "" 
    while True:

        cloud_led_state = check_cloud_led_state()
        message = check_cloud_message()

        if message != "NULL" and message != last_message:
            ser.write(message.encode())  
            last_message = message
            send_message = 1

        if send_message == 1:
            send_message = 0
        
        if cloud_led_state == 1:
            ser.write(b'A') 
            print("LED turned ON - cloud")
        elif cloud_led_state == 0:
            ser.write(b'S') 
            print("LED turned OFF - cloud")

        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data.startswith("Temperatura celsius: "):
                temperature = data.split(": ")[1]
                try:
                    response = requests.post("https://gloriais.azurewebsites.net/update_temperature", data={"temperature": temperature})
                    if response.status_code == 200:
                        print("Temperature data sent successfully to the Azure web app.")
                    else:
                        print(f"Failed to send temperature data to the Azure web app. Status code: {response.status_code}")
                except Exception as e:
                    print("Error sending temperature data:", e)
            elif data == "Inundatie detectata!":
                print("Alert, Flood detected !")
                send_notification()
       
if __name__ == "__main__":
    print("Starting serial communication...")
    read_serial_and_send_data()