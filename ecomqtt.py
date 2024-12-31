import hashlib
import hmac
import requests
import time
import paho.mqtt.client as mqtt
from threading import Timer

# Configuration
ACCESS_KEY = "INSERT_ECOFLOW_KEY"
SECRET_KEY = "INSERT_ECOFLOW_SECRET"
HOST = "https://api.ecoflow.com"
DEVICE_SN = "INSERT_ECOFLOW_SN_SHP2_OR_DPU"

# MQTT Configuration
MQTT_BROKER = "HOME_ASSISTANT_IP"
MQTT_PORT = 1883
MQTT_USERNAME = "INSERT_MQTT_USER"
MQTT_PASSWORD = "INSERT_MQTT_PW"
MQTT_BASE_TOPIC = "/EcoFlow"

# MQTT Client setup
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)


def generate_signature(params, access_key, secret_key, nonce, timestamp):
    # Sort parameters by ASCII value and concatenate them
    sorted_params = "&".join(f"{key}={value}" for key, value in sorted(params.items()))

    # Concatenate accessKey, nonce, and timestamp
    str_to_sign = f"{sorted_params}&accessKey={access_key}&nonce={nonce}&timestamp={timestamp}"

    # Create HMAC-SHA256 signature
    sign_bytes = hmac.new(secret_key.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()

    # Convert to hexadecimal string
    signature = sign_bytes.hex()

    return signature


def get_timestamp():
    return str(int(time.time() * 1000))


def get_nonce():
    return str(int(time.time()))[-6:]


def publish_data():
    nonce = get_nonce()
    timestamp = get_timestamp()

    # Parameters for querying device quota (battery level, input power, output power)
    params = {
        "sn": DEVICE_SN,
        "params": {
            "cmdSet": 32,
            "id": 66,
            "quotas": ["hs_yj751_pd_appshow_addr.inHvMpptPwr"]
        }
    }

    # Flatten the parameters for signature
    flat_params = {
        "sn": DEVICE_SN,
        "params.cmdSet": 32,
        "params.id": 66,
        "params.quotas[0]":"hs_yj751_pd_appshow_addr.inHvMpptPwr"
    }

    all_params = {
        "sn": DEVICE_SN
    }

    # Generate the signature
    sign = generate_signature(all_params, ACCESS_KEY, SECRET_KEY, nonce, timestamp)

    headers = {
        "accessKey": ACCESS_KEY,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": sign,
        "Content-Type": "application/json;charset=UTF-8"
    }

    # URL for querying device data
    url = f"{HOST}/iot-open/sign/device/quota/all"

    # Send POST request
    response = requests.post(url, headers=headers, json=params)

    if response.status_code == 200:
        data = response.json()
        if data['code'] == '0':
            # Extracting the data
            soc = data['data'].get("pd.soc")
            watts_in_sum = data['data'].get("pd.wattsInSum")
            output_watts = data['data'].get("inv.outputWatts")

            # Publish data to separate MQTT topics
            mqtt_client.publish(MQTT_BASE_TOPIC + "battery", 1)
            mqtt_client.publish(MQTT_BASE_TOPIC + "input", 1)
            mqtt_client.publish(MQTT_BASE_TOPIC + "output", 1)

            print(f"Published Battery SOC: {soc}%")
            print(f"Published Input Power: {watts_in_sum} W")
            print(f"Published Output Power: {output_watts} W")
        else:
            print("Error from Ecoflow:", data['message'])
    else:
        print("Failed:", response.status_code, response.text)

    # Schedule the next publish in 60 seconds
    Timer(60, publish_data).start()


if __name__ == "__main__":
    # Connect to MQTT broker
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    # Start publishing data every minute
    publish_data()
