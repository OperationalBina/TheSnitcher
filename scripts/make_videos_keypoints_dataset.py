"""this script takes a folder containing videos and for each frame saves a images with prediction,
a json with the key points, and a pickle with the full prediction"""

import json
import os
import pickle

import cv2
import numpy as np

from src.algorithems import PoseEstimator


def decompose_single_vid(vid_path, file_name, output_dir):
    """
    runs the pose estimation on each frame of a given video

    Args:
        vid_path: path to the video file
        file_name: under what file name to save the frames
        output_dir: path to dir where to save the images and stuff

    Returns:

    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pe = PoseEstimator(threshold=0.5)

    cap = cv2.VideoCapture(vid_path)

    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_num = 1

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f'\rworking on frame {frame_num}/{num_frames}', end='', flush=True)
            try:
                prediction = pe.get_full_prediction(frame)

                # save frame
                frame_path = os.path.join(output_dir, f'{file_name}_frame_{frame_num}_pred.jpg')
                pred_frame = pe.draw_prediction_on_image(frame, prediction)
                cv2.imwrite(frame_path, pred_frame[:, :, ::-1])

                # save predication
                prediction_path = os.path.join(output_dir, f'{file_name}_frame_{frame_num}_pred.pkl')
                with open(prediction_path, 'bw') as f:
                    pickle.dump(prediction, f)

                # save key points of the most confident prediction
                conf_pred_idx = np.argmax(prediction.scores)
                key_points = prediction.pred_keypoints[conf_pred_idx]
                key_points_dict = {'x': key_points[:, 0].tolist(),
                                   'y': key_points[:, 1].tolist(),
                                   'v': key_points[:, 2].tolist()}
                keypoints_path = os.path.join(output_dir, f'{file_name}_frame_{frame_num}_keypoints.json')
                with open(keypoints_path, 'w') as json_file:
                    json.dump(key_points_dict, json_file)

            except Exception as e:
                print(f'something went wrong: {str(e)}')

            frame_num += 1

        else:
            break

    cap.release()
    cv2.destroyAllWindows()


def main(vids_dir, output_dir):
    """
    runs the pose estimation on each frame of each video in a given dir and save the output to a unique folder
    for each video

    Args:
        vids_dir: path to dir that contains video files only!
        output_dir: path to output dir

    Returns:

    """
    for vid_file in os.listdir(vids_dir):
        print(f'working on file {vid_file}')
        vid_path = os.path.join(vids_dir, vid_file)

        file_name = os.path.splitext(vid_file)[0]
        vid_output_dir = os.path.join(output_dir, file_name)

        try:
            decompose_single_vid(vid_path, file_name, vid_output_dir)
        except Exception as e:
            print(f'something went wrong: {str(e)}')

        print()


if __name__ == '__main__':
    Vid_folder = '../data/exmaple'
    Output_folder = '../outputs/keypoints_datasets'

    main(Vid_folder, Output_folder)
