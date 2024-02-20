import joblib  #
import requests
import pandas as pd
from sklearn.linear_model import LinearRegression
import schedule
import time
import json
from requests import get
import time
import numpy as np




def make_predictions():
    loaded_model = joblib.load('svr_model.joblib')  


    url_lux = "http://homeassistant.local:8123/api/states/sensor.esp32_1_tcs34725_illuminance"
    headers = {"Authorization": Authorization }
    data_lux = get(url_lux,headers=headers)

    data_lux=data_lux.text
    data_lux= json.loads(data_lux)
    print("--------------------------------")
    print(data_lux)
    print("----------------------------")
    #brightness_value = data_lux['state']


    lux_state = pd.to_numeric(data_lux['state'], errors='coerce')
    X = [[lux_state]]
    

    
    if lux_state >= 1200:
    # Construct the data for the Home Assistant service call
        data = {
        "entity_id": "light.yeelight_colorb_0xed3b956",
        "brightness": 0,  # You can use lux_state directly if it's numeric
  
    }

    # URL and headers for Home Assistant API call
        url_light = "http://homeassistant.local:8123/api/services/light/turn_on"  # Fixed URL and casing
        headers = {
        "Authorization": Authorization,
        "Content-Type": "application/json",
    }

    # Send the API POST request to turn on the light
        response = requests.post(url_light, json=data, headers=headers)
        print(response.text)

    # Check the response (you can log or handle errors here)
        if response.status_code == 200:
            print("API POST successful.")
        else:
            print(f"API POST failed with status code: {response.status_code}")
    else:
        predictions = loaded_model.predict(X) 
        predictions_list = predictions.tolist()
        predictions_list = int(predictions_list[0][0]) 
    



        data = {
        "entity_id": "light.yeelight_colorb_0xed3b956",
        "brightness": str(predictions_list),
    
    }
        print(data)

    # Send the API POST request
        url_light = "http://homeassistant.local:8123/api/services/light/TURN_ON"
        headers = {
        "Authorization":  Authorization,
        "Content-Type": "application/json",
    }

        response = requests.post(url_light, json=data, headers=headers)
        print(response.text)

    # Check the response (you can log or handle errors here)
        if response.status_code == 200:
            print("API POST successful.")
        else:
            print(f"API POST failed with status code: {response.status_code}")
    
   

# Schedule the prediction and API posting every 5 minutes
schedule.every(1).minutes.do(make_predictions)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)

