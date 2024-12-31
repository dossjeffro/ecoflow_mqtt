I didn't see support for Ecoflow Delta Pro Ultra or Smart Home Panel 2 for Home Assistant. So, I wrote my own.

Steps to setup. (This is by memory and it has been a month, but this should be complete)

1. Install MQTT on Home Assistant. Make sure you add user/password. - I'm not an expert on Home Assistant, so follow others instructions on this. 
Just make sure you remember the user and password is it will be needed in the python.

2. Add sensors to your Home Assistant configuration YAML 
NOTE: I have a leading slash in the MQTT topics which I don't think is the correct nomenclature. But, it works for me.

'''yaml
mqtt:
  sensor:
    - name: "EcoFlow Battery"
      state_topic: "/home/ecoflow/battery"
    - name: "EcoFlow HighPV"
      state_topic: "/home/ecoflow/PvHvPwr"
      unit_of_measurement: "W"
      state_class: measurement
    - name: "EcoFlow LowPV"
      state_topic: "/home/ecoflow/PvLvPwr"
      unit_of_measurement: "W"
      state_class: measurement
'''


3. Request an Ecoflow API Key. I did not get a confirmation that one was created. I just kept checking and eventually they provided one.
Copy the clientid and key. You can request the Developer key here: https://developer.ecoflow.com/us

4. Snag the Serial Number(s) from your Ecoflow devices. You can find them in your Ecoflow app under the device's "Specifications". (At the top.)
