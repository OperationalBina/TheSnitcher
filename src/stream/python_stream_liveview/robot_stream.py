import queue
import sys
import threading
import time
import numpy as np
import cv2

sys.path.append('../decoder/output/')
sys.path.append('../../connection/')


import enum
import robot_connection
import libh264decoder
# import PoseEstimation

class ConnectionType(enum.Enum):
    WIFI_DIRECT = 1
    WIFI_NETWORKING = 2
    USB_DIRECT = 3


class RobotLiveview(object):
    WIFI_DIRECT_IP = '192.168.2.1'
    WIFI_NETWORKING_IP = ''
    USB_DIRECT_IP = '192.168.42.2'

    def __init__(self, connection_type, Pose):
        """
        Inputs:
         - connection_type: is according ConnectionType class
         - Pose: is a PoseEstimation instance
         - frame_queue: queue to push frames to
        """
        self.connection = robot_connection.RobotConnection()
        self.connection_type = connection_type

        self.video_decoder = libh264decoder.H264Decoder()
        libh264decoder.disable_logging()

        self.video_decoder_thread = threading.Thread(target=self._video_decoder_task)
        self.video_decoder_msg_queue = queue.Queue(64)
        self.video_display_thread = threading.Thread(target=self._video_display_task)

        self.command_ack_list = []

        self.is_shutdown = True
        self.api_json = []
        self.pose = Pose

    def open(self):
        if self.connection_type is ConnectionType.WIFI_DIRECT:
            self.connection.update_robot_ip(RobotLiveview.WIFI_DIRECT_IP)
        elif self.connection_type is ConnectionType.USB_DIRECT:
            self.connection.update_robot_ip(RobotLiveview.USB_DIRECT_IP)
        elif self.connection_type is ConnectionType.WIFI_NETWORKING:
            robot_ip = self.connection.get_robot_ip(timeout=10)
            if robot_ip:
                self.connection.update_robot_ip(robot_ip)
            else:
                print('Get robot failed')
                return False
        self.is_shutdown = not self.connection.open()

    def close(self):
        self.is_shutdown = True
        self.video_decoder_thread.join()
        self.video_display_thread.join()
        self.connection.close()


    def display(self):
        print(f'shut down status: {self.is_shutdown}')
        self.command('command')
        time.sleep(1)
        self.command('stream on')

        self.video_decoder_thread.start()
        self.video_display_thread.start()

        print('display!')

    def command(self, msg):
        # TODO: TO MAKE SendSync()
        #       CHECK THE ACK AND SEQ
        self.connection.send_data(msg)

    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.video_decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, int(ls / 3), 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

    def _video_decoder_task(self):
        print('video_decoder')
        package_data = b''

        self.connection.start_video_recv()

        while not self.is_shutdown:
            buff = self.connection.recv_video_data()
            if buff:
                package_data += buff
                if len(buff) != 1460:
                    for frame in self._h264_decode(package_data):
                        try:
                            self.video_decoder_msg_queue.put(frame, timeout=2)
                        except Exception as e:
                            if self.is_shutdown:
                                break
                            print('video decoder queue full')
                            continue
                    package_data = b''

        self.connection.stop_video_recv()

    def _video_display_task(self):
        print('video_display')
        print(f'sutdown status in video_display is: {self.is_shutdown}')
        while not self.is_shutdown:
            try:
                frame = self.video_decoder_msg_queue.get(timeout=2)
            except Exception as e:
                if self.is_shutdown:
                    break
                print('video decoder queue empty')
                continue
            img = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            self.api_json = self.pose(img)
