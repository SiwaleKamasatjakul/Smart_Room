from transformers import pipeline
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import time
import requests
import schedule
from datetime import datetime
import paho.mqtt.client as mqtt




client = mqtt.Client()
client.username_pw_set(username, password)

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Define the MQTT topic to publish to
topic = "camera\counting_people"

# Publish the message to the MQTT topic


# Load font
font = ImageFont.truetype("arial.ttf", 40)

# Initialize the object detection pipeline
object_detector = pipeline("object-detection", model="hustvl/yolos-tiny")


        
# Draw bounding box definition
def draw_bounding_box(im, score, label, xmin, ymin, xmax, ymax, index, num_boxes):
    """ Draw a bounding box. """
    print(f"Drawing bounding box {index} of {num_boxes}...")

    # Draw the actual bounding box
    im_with_rectangle = ImageDraw.Draw(im)
    im_with_rectangle.rounded_rectangle((xmin, ymin, xmax, ymax), outline="red", width=5, radius=10)

    # Draw the label
    im_with_rectangle.text((xmin + 35, ymin - 25), label, fill="white", stroke_fill="red", font=font)

    # Return the intermediate result
    return im



while True:
    
    #cap = cv2.VideoCapture(rtsp_url)
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the OpenCV frame to a PIL image
    im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Perform object detection
    bounding_boxes = object_detector(im)

    # Iteration elements
    num_boxes = len(bounding_boxes)
    index = 0

    # Initialize count of people
    person_count = 0
    print('start loop')
    print(person_count)
    # Draw bounding box for each result and count people
    for bounding_box in bounding_boxes:
        label = bounding_box["label"]

        # Check if the label corresponds to a person
        if label.lower() == "person":
            person_count += 1

        # Get actual box
        box = bounding_box["box"]

        # Draw the bounding box
        im = draw_bounding_box(im, bounding_box["score"], label,
                               box["xmin"], box["ymin"], box["xmax"], box["ymax"], index, num_boxes)

        # Increase index by one
        index += 1

    # Convert the PIL image back to OpenCV format for display
    frame = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display the count of people
    cv2.putText(frame, f"Number of people detected: {person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Object Detection", frame)
    client.publish(topic, person_count)
    client.loop_start()

# Publish the message
    client.publish(topic, person_count)

# Optionally, you can wait or perform other tasks here

# Disconnect from the MQTT broker when done
    client.loop_stop()
    print(current_time)
    print(person_count)
    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    #time.sleep(frame_delay)
    #check_and_make_predictions(person_count)




# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)


    # Display the frame
 

# Release video capture and close OpenCV windows
cap.release()
cv2.destroyAllWindows()







