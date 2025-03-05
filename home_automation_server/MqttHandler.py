from typing import Callable, Any, TypeAlias

import paho.mqtt.client as mqtt
from paho.mqtt.client import PayloadType, ConnectFlags, DisconnectFlags
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.enums import CallbackAPIVersion

UserData: TypeAlias = Any  # type: ignore[explicit-any]
Message: TypeAlias = mqtt.MQTTMessage
MessageHandler: TypeAlias = Callable[[mqtt.Client, UserData, Message], None]


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

        self._on_message_handlers: list[MessageHandler] = []
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
            for message_handler in self._on_message_handlers:
                message_handler(client, userdata, msg)

        return on_message_handler

    def add_message_handler(self, handler: MessageHandler) -> None:
        self._on_message_handlers.append(handler)

    def publish(
        self,
        topic: str,
        payload: PayloadType = None,
        qos: int = 0,
        retain: bool = False,
        properties: Properties | None = None,
    ) -> None:
        self.mqtt_client.publish(topic, payload, qos, retain, properties)
