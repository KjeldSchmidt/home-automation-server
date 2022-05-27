import paho.mqtt.client as mqtt

Client = mqtt.Client


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("zigbee2mqtt/#")


def on_disconnect(client, userdata, rc):
    print(f"Disconnected from mqtt network with code {rc}")


def get_client() -> mqtt.Client:
    client = mqtt.Client("HomeAutomationServer", clean_session=False)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()
    return client
