#!python3

import os
import signal
import sys
from flask import Flask, jsonify
import socket
import fcntl
import struct
from camera_stream import CameraLiveview
from robot_stream import RobotLiveview, ConnectionType

import PoseEstimation


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                        struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])


def test():
    app = Flask(__name__)
    HOST_IP = str(get_ip_address('eth0'))
    HOST_PORT = 5000
    pose_model = PoseEstimation.PoseEstimation()
    try:
        stream_kind = os.environ['STREAM_KIND']
    except KeyError:
        print("Please set the environment variable STREAM_KIND")
        sys.exit(1)
    if stream_kind == 'ROBOT':
        stream = RobotLiveview(ConnectionType.USB_DIRECT, pose_model)
    elif stream_kind == 'CAMERA':
        stream = CameraLiveview(pose_model)
    else:
        print('Environment variable STREAM_KIND has to be ROBOT or CAMERA')
        sys.exit(1)

    def exit(signum, frame):
        stream.close()

    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGTERM, exit)
    stream.open()
    stream.display()

    @app.route('/', methods=['GET'])
    def get_alert():
        return jsonify(stream.api_json)

    app.run(host=HOST_IP, port=HOST_PORT)


if __name__ == '__main__':
    test()
