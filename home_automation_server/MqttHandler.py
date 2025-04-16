import dataclasses
import json
from typing import Callable, Any, TypeAlias

import paho.mqtt.client as mqtt
from paho.mqtt.client import PayloadType, ConnectFlags, DisconnectFlags
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.enums import CallbackAPIVersion

UserData: TypeAlias = Any  # type: ignore[explicit-any]
Message: TypeAlias = mqtt.MQTTMessage
MessageHandler: TypeAlias = Callable[[mqtt.Client, UserData, Message], None]


@dataclasses.dataclass
class RegisteredMessageHandler:
    callback: MessageHandler
    topic: str | None


class MqttHandler:
    def __init__(self) -> None:
        mqtt_client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION1,
            client_id="HomeAutomationServer",
            clean_session=False,
        )
        mqtt_client.on_connect = self._on_connect_handler
        mqtt_client.on_disconnect = self._on_disconnect_handler
        mqtt_client.on_message = self._make_on_message_handler()
        mqtt_client.connect("127.0.0.1", 1883, 60)
        mqtt_client.loop_start()

        self._on_message_handlers: list[RegisteredMessageHandler] = []
        self.mqtt_client = mqtt_client

    @staticmethod
    def _on_connect_handler(
        client: mqtt.Client,
        userdata: UserData,
        flags: ConnectFlags,
        rc: ReasonCode,
        properties: Properties | None = None,
    ) -> None:
        print(f"Connected to mqtt network with result code {rc}")
        client.subscribe("zigbee2mqtt/#")

    @staticmethod
    def _on_disconnect_handler(
        client: mqtt.Client,
        userdata: UserData,
        dc_flags: DisconnectFlags,
        rc: ReasonCode,
        properties: Properties | None,
    ) -> None:
        print(f"Disconnected from mqtt network with code {rc}")

    def _make_on_message_handler(self) -> MessageHandler:
        # To access the list of all message handlers, we need `self` to be available to the mqtt.Client.
        # To achieve this, we create the handler as a closure, binding self to the handler permanently.
        def on_message_handler(client: mqtt.Client, userdata: UserData, msg: mqtt.MQTTMessage) -> None:
            print(f"Received Mqtt message, topic: {msg.topic}, msg: {msg.payload.decode()}")
            for registered_message_handler in self._on_message_handlers:
                if registered_message_handler.topic not in [msg.topic, None]:
                    continue

                payload: str = msg.payload.decode()
                payload_dict = json.loads(payload)
                registered_message_handler.callback(client, userdata, payload_dict)

        return on_message_handler

    def add_message_handler(self, handler: MessageHandler, topic: str = None) -> None:
        new_registered_handler = RegisteredMessageHandler(callback=handler, topic=topic)
        self._on_message_handlers.append(new_registered_handler)

    def publish(
        self,
        topic: str,
        payload: PayloadType = None,
        qos: int = 0,
        retain: bool = False,
        properties: Properties | None = None,
    ) -> None:
        self.mqtt_client.publish(topic, payload, qos, retain, properties)
