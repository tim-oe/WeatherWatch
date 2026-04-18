import json

import paho.mqtt.client as mqtt
from conf.AppConfig import AppConfig
from conf.MqttConfig import MqttConfig
from entity.SolarReading import SolarReading
from entity.TemperatureReading import TemperatureReading
from py_singleton import singleton
from repository.SolarReadingRepository import SolarReadingRepository
from repository.TemperatureReadingRepository import TemperatureReadingRepository
from util.Logger import logger

__all__ = ["MqttListener"]


@logger
@singleton
class MqttListener:
    """
    mqtt listener
    subscribes to solar and temperature topics and persists readings
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._config: MqttConfig = AppConfig().mqtt
        self._solar_repo: SolarReadingRepository = SolarReadingRepository()
        self._temperature_repo: TemperatureReadingRepository = TemperatureReadingRepository()
        self._client: mqtt.Client = None

    def start(self):
        """
        connect to broker and start listening
        :param self: this
        """
        if not self._config.enable:
            self.logger.info("mqtt disabled")
            return

        self.logger.info("connecting to mqtt broker %s:%s", self._config.host, self._config.port)

        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if self._config.username:
            self._client.username_pw_set(self._config.username, self._config.password)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        self._client.connect(self._config.host, self._config.port)
        self._client.loop_start()

    def stop(self):
        """
        disconnect from broker
        :param self: this
        """
        if self._client is not None:
            self._client.loop_stop()
            self._client.disconnect()
            self.logger.info("mqtt disconnected")

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """
        on connect callback
        :param self: this
        """
        self.logger.info("mqtt connected reason_code=%s", reason_code)

        client.subscribe(self._config.solar_topic)
        self.logger.info("subscribed to %s", self._config.solar_topic)

        client.subscribe(self._config.temperature_topic)
        self.logger.info("subscribed to %s", self._config.temperature_topic)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        """
        on disconnect callback
        :param self: this
        """
        self.logger.warning("mqtt disconnected reason_code=%s", reason_code)

    def _on_message(self, client, userdata, msg):
        """
        on message callback - routes to the appropriate handler
        :param self: this
        """
        self.logger.debug("received message on %s", msg.topic)

        try:
            payload: dict = json.loads(msg.payload.decode("utf-8"))

            if msg.topic == self._config.solar_topic:
                self._handle_solar(payload)
            elif msg.topic == self._config.temperature_topic:
                self._handle_temperature(payload)
            else:
                self.logger.warning("unhandled topic %s", msg.topic)
        except Exception:
            self.logger.exception("failed to process mqtt message on %s", msg.topic)

    def _handle_solar(self, data: dict):
        """
        process solar reading from mqtt payload
        :param self: this
        :param data: the json payload
        """
        self.logger.debug("processing solar reading")

        ent = SolarReading.from_dict(data, type="solar", name="solar")

        self._solar_repo.insert(ent)
        self.logger.debug("inserted solar reading id=%s", ent.id)

    def _handle_temperature(self, data: dict):
        """
        process temperature reading from mqtt payload
        :param self: this
        :param data: the json payload
        """
        self.logger.debug("processing temperature reading")

        ent = TemperatureReading.from_dict(data, type="temperature", name="temperature", unit="C")

        self._temperature_repo.insert(ent)
        self.logger.debug("inserted temperature reading id=%s", ent.id)
