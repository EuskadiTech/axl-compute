import machine
import time
import ubinascii
import json
import network
import socket
from time import sleep
from umqtt.simple import MQTTClient
    
# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "node": "ES48920-MP-001",
    "ap_name": "Gameme 2.4G",
    "ap_pass": "D9RFYKCA76PFYXH4",
    "broker": "",
    "port": 0,
    "user": "",
    "passw": "",
    "ssl": True,
    "client_id": b"micropython_" + ubinascii.hexlify(machine.unique_id()),
    "topic": b"home",
}
def safe_serialize(obj):
  default = lambda o: f"<non-serializable: {type(o).__qualname__}>"
  return json.dumps(obj, default=default)

client = None
def sub_cb(topic, msg):
    print(msg)
    print(topic)
    ms = json.loads(msg.decode("utf-8"))
    if ms["type"] == "python-inline":
        loc = {}
        try:
          exec(ms["script"], globals(), loc)
          client.publish(ms["out-topic"], safe_serialize(loc))
        except Exception as e:
          client.publish(ms["out-topic"], safe_serialize({"_err": str(e)}))
    elif ms["type"] == "cmd":
        client.publish(ms["out-topic"], safe_serialize({"_err": str("This is a MicroPython node, the cmd type is not compatible.")}))
    print(msg.topic+" "+str(ms))
    
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(CONFIG["ap_name"], CONFIG["ap_pass"])
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig())
def main():
    client = MQTTClient(CONFIG['client_id'], CONFIG['broker'], CONFIG["port"], CONFIG["user"], CONFIG["passw"], 0, CONFIG["ssl"])
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(f"axlcore/node/{CONFIG['node']}".encode("utf-8"))
    print("Connected to {}".format(CONFIG['broker']))
    while True:
        if True:
            # Blocking wait for message
            c.wait_msg()
        else:
            # Non-blocking wait for message
            c.check_msg()
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            time.sleep(1)

if __name__ == '__main__':
    try:
        connect()
    except KeyboardInterrupt:
        machine.reset()
    main()
