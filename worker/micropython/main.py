import machine
import time
import ubinascii

from umqtt.simple import MQTTClient

# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "broker": "",
    "user": "",
    "passw": "",
    "ssl": True,
    "client_id": b"micropython_" + ubinascii.hexlify(machine.unique_id()),
    "topic": b"home",
}

client = None
def sub_cb(topic, msg):
    print((topic, msg))
  
def main():
    client = MQTTClient(CONFIG['client_id'], CONFIG['broker'], CONFIG["port"], CONFIG["user"], CONFIG["passw"], 0, CONFIG["ssl"])
    client.set_callback(sub_cb)
    client.connect()
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
    main()
