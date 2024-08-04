import paho.mqtt.client as mqtt
import json
import subprocess

NODE = env["AXL_NODE"]
MQUSER = env["AXL_MQUSER"]
MQPASS = env["AXL_MQPASS"]
MQHOST = env["AXL_MQHOST"]
MQPORT = int(env["AXL_MQPORT"])
MQTLS = env.get("AXL_MQTLS")
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f"axlcore/node/{NODE}")
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# The callback for when a PUBLISH message is received from the server.
def safe_serialize(obj):
  default = lambda o: f"<<non-serializable: {type(o).__qualname__}>>"
  return json.dumps(obj, default=default)

def on_message(client, userdata, msg):
    ms = json.loads(msg.payload.decode("utf-8"))
    if ms["type"] == "python-inline":
        loc = {}
        exec(ms["script"], globals(), loc)
        client.publish(ms["out-topic"], safe_serialize(loc))
    elif ms["type"] == "cmd":
        e = subprocess.check_output(ms["script"], shell=True)
        client.publish(ms["out-topic"], safe_serialize({"out": e.decode("utf-8")}))
    print(msg.topic+" "+str(ms))


mqttc.on_connect = on_connect
mqttc.on_message = on_message
if MQTLS == "1":
  mqttc.tls_set()
mqttc.username_pw_set(MQUSER, MQPASS)

mqttc.connect(MQHOST, MQPORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()
