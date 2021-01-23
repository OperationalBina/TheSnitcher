"""get the model prediction for each frame of the video and save as a pkl"""
import os
import pickle

import cv2

from src.algorithems import PoseEstimator


def main(vid_path, output_path):
    pe = PoseEstimator()

    cap = cv2.VideoCapture(vid_path)

    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_num = 1

    predictions = []

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f'\rworking on frame {frame_num}/{num_frames}', end='', flush=True)
            prediction = pe.get_full_prediction(frame)

            predictions.append(prediction)

            frame_num += 1

        else:
            break

    cap.release()
    cv2.destroyAllWindows()

    # save pickle
    with open(output_path, 'bw') as f:
        pickle.dump(predictions, f)


if __name__ == '__main__':
    Data_dir = '../data'
    Output_dir = '../outputs'
    Vid_file = '1_DJI_0277.MOV'
    Vid_path = os.path.join(Data_dir, Vid_file)
    Output_path = os.path.join(Output_dir, f'{Vid_file[:-4]}_preds.pkl')
    print(Output_path)
    main(Vid_path, Output_path)
