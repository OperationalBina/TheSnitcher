"""this script takes a folder containing images and for each image saves a images with prediction,
a json with the key points, and a pickle with the full prediction"""

import json
import os
import pickle

import cv2
import numpy as np

from src.algorithems import PoseEstimator


def decompose_single_image(image_path, file_name, output_dir):
    """
    runs the pose estimation on image

    Args:
        image_path: path to the video file
        file_name: under what file name to save the frames
        output_dir: path to dir where to save the images and stuff

    Returns:

    """
    pe = PoseEstimator(threshold=0.5)

    img = cv2.imread(image_path)

    prediction = pe.get_full_prediction(img)

    # save frame
    frame_path = os.path.join(output_dir, f'{file_name}_pred.jpg')
    pred_frame = pe.draw_prediction_on_image(img, prediction)
    cv2.imwrite(frame_path, pred_frame[:, :, ::-1])

    # save predication
    prediction_path = os.path.join(output_dir, f'{file_name}_pred.pkl')
    with open(prediction_path, 'bw') as f:
        pickle.dump(prediction, f)

    # save key points of the most confident prediction
    conf_pred_idx = np.argmax(prediction.scores)
    key_points = prediction.pred_keypoints[conf_pred_idx]
    key_points_dict = {'x': key_points[:, 0].tolist(),
                       'y': key_points[:, 1].tolist(),
                       'v': key_points[:, 2].tolist()}
    keypoints_path = os.path.join(output_dir, f'{file_name}_keypoints.json')
    with open(keypoints_path, 'w') as json_file:
        json.dump(key_points_dict, json_file)


def main(imgs_dir, output_dir):
    """
    runs the pose estimation on each image in a given dir and save the output dir

    Args:
        imgs_dir: path to dir that contains images files only!
        output_dir: path to output dir

    Returns:

    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for img_file in os.listdir(imgs_dir):
        print(f'working on file {img_file}')
        vid_path = os.path.join(imgs_dir, img_file)

        file_name = os.path.splitext(img_file)[0]

        decompose_single_image(vid_path, file_name, output_dir)


if __name__ == '__main__':
    Images_folder = '../data/synth_aim'
    Output_folder = '../outputs/keypoints_datasets/synth_aim'

    main(Images_folder, Output_folder)
