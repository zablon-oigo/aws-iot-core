import time
from datetime import datetime, timezone
import json
import ssl
import _thread
import paho.mqtt.client as mqtt

AWS_ENDPOINT = " "
TOPIC = "data"

def on_connect(client, userdata, flags, rc):
    print("Connected to AWS IoT Core, rc =", rc)

client = mqtt.Client(
    client_id="distance-simulator",
    protocol=mqtt.MQTTv311,
    transport="tcp"
)
client.on_connect = on_connect

client.tls_set(
    ca_certs="./root-CA.crt",
    certfile="./certificate.pem.crt",
    keyfile="./private.pem.key",
    tls_version=ssl.PROTOCOL_TLSv1_2
)

client.tls_insecure_set(False)
client.connect(AWS_ENDPOINT, 8883, 60)

distances = [50,45,40,35,30,35,25,24,23,22,22,20,15,10,9,7,5,1]

def publishData(txt):
    print(txt)
    while True:
        for d in distances + list(reversed(distances)):
            status = "GREEN" if d >= 25 else "YELLOW" if d >= 10 else "RED"
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "distance_cm": d,
                "status": status
            }
            print("Publishing:", payload)
            client.publish(TOPIC, json.dumps(payload), qos=1)
            time.sleep(5)

_thread.start_new_thread(publishData, ("Simulator started",))
client.loop_forever()
