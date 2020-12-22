#!python3

import os
import signal
import sys
from flask import Flask, jsonify
import socket
import fcntl
import struct
# try
from camera_stream import CameraLiveview
from robot_stream import RobotLiveview, ConnectionType
import multiprocessing

import PoseEstimation


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                        struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])


def frame_processing(stream, queue, pose):
    """
    Opens a process for reading frames and processing them. Updating the stream
    attribute api_json according to alerts

    Inputs:
     - stream: stream object (robot ore camera)
     - queue: shared queue for pushing and getting frame
     - pose: pose estimation model
    """
    p = multiprocessing.Process(target=stream.display)
    p.start()
    while True:
        frame = queue.get()
        stream.api_json = pose(frame)


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
    frame_queue = multiprocessing.Queue(1)
    if stream_kind == 'ROBOT':
        stream = RobotLiveview(ConnectionType.USB_DIRECT, frame_queue)

        def exit(signum, frame):
            stream.close()

        signal.signal(signal.SIGINT, exit)
        signal.signal(signal.SIGTERM, exit)
        stream.open()
        # stream.display()
        frame_processing(stream, frame_queue, pose_model)
    elif stream_kind == 'CAMERA':
        stream = CameraLiveview()
        stream.display()
    else:
        print('Environment variable STREAM_KIND has to be ROBOT or CAMERA')
        sys.exit(1)

    @app.route('/', methods=['GET'])
    def get_alert():
        return jsonify(stream.api_json)

    app.run(host=HOST_IP, port=HOST_PORT)


if __name__ == '__main__':
    test()
