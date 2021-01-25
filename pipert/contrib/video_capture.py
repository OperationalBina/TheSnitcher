from pipert.core import BaseComponent
from pipert.contrib.routines import listen_to_stream, message_to_redis


class VidCapture(BaseComponent):
    def __init__(self, component_config, start_component=False):
        super().__init__(component_config, start_component)