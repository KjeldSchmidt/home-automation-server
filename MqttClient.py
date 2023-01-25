from typing import Callable, Any, TypeAlias

import paho.mqtt.client as mqtt

Client = mqtt.Client
Message: TypeAlias = mqtt.MQTTMessage


class MqttClient:
    def __init__(self) -> None:
        client = mqtt.Client("HomeAutomationServer", clean_session=False)
        client.on_connect = self._on_connect()
        client.on_disconnect = self._on_disconnect()
        client.on_message = self._on_message()
        client.connect("127.0.0.1", 1883, 60)
        client.loop_start()

        self._on_message_handlers: list[Callable[[Client, Any, Message], None]] = []
        self.publish = client.publish

    @staticmethod
    def _on_connect():
        def on_connect(client: Client, userdata, flags, rc):
            print(f"Connected to mqtt network with result code {rc}")
            client.subscribe("zigbee2mqtt/#")

        return on_connect

    @staticmethod
    def _on_disconnect():
        def on_disconnect(client: Client, userdata, rc):
            print(f"Disconnected from mqtt network with code {rc}")

        return on_disconnect

    def _on_message(self):
        def on_message(client: Client, userdata: Any, msg: mqtt.MQTTMessage):
            print(f"Received Mqtt message, topic: {msg.topic}, msg: {msg.payload}")
            for message_handler in self._on_message_handlers:
                message_handler(client, userdata, msg)

        return on_message

    def add_message_handler(
        self, handler: Callable[[Client, Any, Message], None]
    ) -> None:
        self._on_message_handlers.append(handler)
