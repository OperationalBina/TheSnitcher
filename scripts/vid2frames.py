"""a script for breaking a video to individial frames"""
import os

import cv2


def main(vid_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.split(vid_path)[-1][:-4]

    cap = cv2.VideoCapture(vid_path)

    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_num = 1

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f'\rworking on frame {frame_num}/{num_frames}', end='', flush=True)
            frame_path = os.path.join(output_dir, f'{file_name}_frame_{frame_num}.jpg')

            cv2.imwrite(frame_path, frame)

            frame_num += 1
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    Data_dir = '../data/sim'
    Vid_file = 'Peek 2021-01-23 18-00.mp4'
    Vid_path = os.path.join(Data_dir, Vid_file)
    Output_dir = os.path.join(Data_dir, f'{Vid_file[:-4]}_frames')
    main(Vid_path, Output_dir)
