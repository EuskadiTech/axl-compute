import machine
import time
import ubinascii
import json
import network
import socket
from time import sleep
from umqtt.simple import MQTTClient
import gc
import ssl
from machine import Pin

led = Pin("LED", Pin.OUT)
led.on()

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_NONE
# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "node": "ES48920-MP-001",
    "ap_name": "",
    "ap_pass": "",
    "broker": "",
    "port": 8883,
    "user": "",
    "passw": "",
    "ssl": context,
    "client_id": b"micropython_" + ubinascii.hexlify(machine.unique_id())
}
def safe_serialize(obj):
    out = {
        "out": obj.get("out"),
        "_err": obj.get("out"),
        "out1": obj.get("out1"),
        "out2": obj.get("out2"),
        "out3": obj.get("out3"),
        "out4": obj.get("out4"),
    }
    return json.dumps(obj)

client = None
def sub_cb(topic, msg):
    gc.collect()
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
    print(str(topic)+" "+str(ms))
    gc.collect()
    led.toggle()
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
    global client
    client = MQTTClient(client_id=CONFIG['client_id'], server=CONFIG['broker'], port=CONFIG["port"], user=CONFIG["user"], password=CONFIG["passw"], ssl=CONFIG["ssl"])
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(f"axlcore/node/{CONFIG['node']}".encode("utf-8"))
    print("Connected to {}".format(CONFIG['broker']))
    while True:
        if True:
            # Blocking wait for message
            client.wait_msg()
        else:
            # Non-blocking wait for message
            client.check_msg()
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            gc.collect()
            time.sleep(1)

if __name__ == '__main__':
    try:
        connect()
    except KeyboardInterrupt:
        machine.reset()
    main()
