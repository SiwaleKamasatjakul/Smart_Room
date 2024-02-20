import cv2
import numpy as np
import pickle
import requests
import face_recognition
from datetime import datetime
import paho.mqtt.client as mqtt
import sys

# MQTT Broker Configuration
broker_address = "******"
broker_port = ****** 
username = "******"
password = "******"

# MQTT Topic
topic = "camera\Recog"

# Telegram Configuration
token = "******"
chat_id = "******"

# File Path for Face Encodings
file_path = r'C:\Users\Meth\Downloads\Compressed\Face-Recognition-master\test\encodingfile'

# Global flag to control the execution of the intruder function
intruder_running = False

# Initialize MQTT Client
client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(broker_address, broker_port)

def send_telegram_message(text, photo=None):
    base_url_photo = f'https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}'
    base_url_ms = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}'
    if photo:
        files = {'photo': open(photo, 'rb')}
        resp = requests.post(base_url_photo, files=files)
    else:
        url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
        resp = requests.get(url_req)
    print(resp.json())

def intruder_detection():
    global intruder_running
    intruder_running = True
    rtsp_url = "******************"
    video_capture = cv2.VideoCapture(rtsp_url)
    encoded = pickle.loads(open(file_path, 'rb').read())
    known_face_encodings = list(encoded.values())        
    known_face_names = list(encoded.keys())
    process_this_frame = True
    while intruder_running:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:,:,::-1])
        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    cv2.imwrite('user.jpg', frame)
                    send_telegram_message('Hello ' + name, 'user.jpg')
                    client.publish(topic, name)
                    intruder_running = False
                face_names.append(name)
        process_this_frame = not process_this_frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            if name == 'Unknown':
                cv2.imwrite('intruder.jpg', frame)
                send_telegram_message("Intruder Detected⚠️⚠️⚠️", 'intruder.jpg')
                intruder_running = False
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()

def on_message(client, userdata, message):
    payload = message.payload.decode('utf-8')
    if payload == "Pushed":
        print("Button pushed. Running intruder detection...")
        intruder_detection()

# Set the on_message callback function
client.on_message = on_message

# Subscribe to the topic
client.subscribe(topic)

# Start the MQTT loop in the background
client.loop_start()
print("Intruder detection started. Listening to MQTT...")

# Run the scheduler
while True:
    pass
