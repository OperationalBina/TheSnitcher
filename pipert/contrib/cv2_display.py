from pipert.core.component import BaseComponent
from queue import Queue
import argparse
import redis
from urllib.parse import urlparse
import zerorpc
import gevent
import signal
from pipert.core.routine import Events
from pipert.core.mini_logics import FramesFromRedis, DisplayCV2
from pipert.core.handlers import tick, tock


class CV2VideoDisplay(BaseComponent):

    def __init__(self, output_key, in_key, redis_url, field):
        super().__init__()

        self.field = field  # .encode('utf-8')
        self.queue = Queue(maxsize=1)
        self.t_get = FramesFromRedis(in_key, redis_url, self.queue, self.field, name="get_frames").as_thread()
        self.register_routine(self.t_get)
        self.t_draw = DisplayCV2(in_key, self.queue, name="draw_frames").as_thread()
        self.register_routine(self.t_draw)

    def flip_im(self):
        self.t_get.flip = not self.t_get.flip

    def negative(self):
        self.t_draw.negative = not self.t_draw.negative


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input stream key name', type=str, default='camera:1')
    parser.add_argument('-u', '--url', help='Redis URL', type=str, default='redis://127.0.0.1:6379')
    parser.add_argument('-z', '--zpc', help='zpc port', type=str, default='4244')
    parser.add_argument('--field', help='Image field name', type=str, default='image')
    args = parser.parse_args()

    # Set up Redis connection
    url = urlparse(args.url)
    conn = redis.Redis(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')

    zpc = CV2VideoDisplay(None, args.input, url, args.field)
    # zpc = zerorpc.Server(CV2VideoDisplay(None, args.input, url, args.field))
    # zpc.bind(f"tcp://0.0.0.0:{args.zpc}")
    zpc._bind_endpoint(f"tcp://0.0.0.0:{args.zpc}")
    print("run")
    # gevent.signal_handler(signal.SIGTERM, zpc.stop)
    zpc.run()
    print("Killed")
