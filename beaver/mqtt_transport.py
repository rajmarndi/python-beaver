import datetime
from mosquitto import Mosquitto

import beaver.transport
from beaver.transport import TransportException


class MosquittoTransport(beaver.transport.Transport):

    def __init__(self, beaver_config, file_config, logger=None):
        """
        Mosquitto client initilization. Once this this transport is initialized
        it has invoked a connection to the server
        """
        super(MosquittoTransport, self).__init__(beaver_config, file_config, logger=logger)

        self._file_config = file_config
        self._client = Mosquitto(beaver_config.get('mqtt_clientid'), clean_session=True)
        self._topic = beaver_config.get('mqtt_topic')
        self._client.connect(
            host=beaver_config.get('mqtt_hostname'),
            port=beaver_config.get('mqtt_port'),
            keepalive=beaver_config.get('mqtt_keepalive')
        )

        def on_disconnect(mosq, obj, rc):
            if rc == 0:
                logger.debug("Mosquitto has successfully disconnected")
            else:
                logger.debug("Mosquitto unexpectedly disconnected")

        self._client.on_disconnect = on_disconnect

    def callback(self, filename, lines, **kwargs):
        """publishes lines one by one to the given topic"""
        timestamp = self.get_timestamp(**kwargs)

        for line in lines:
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    self._client.publish(self._topic, line, 0)
            except Exception, e:
                try:
                    raise TransportException(e.strerror)
                except AttributeError:
                    raise TransportException("Unspecified exception encountered")

    def interrupt(self):
        if self._client:
            self._client.disconnect()

    def unhandled(self):
        return True
