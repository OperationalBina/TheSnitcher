import torch
import json
import trt_pose.coco
import torch
from torch2trt import TRTModule
import cv2
import torchvision.transforms as transforms
import PIL.Image
from trt_pose.parse_objects import ParseObjects


class PoseEstimation:
    def __init__(self, path_model='resnet18_baseline_att_224x224_A_epoch_249_trt.pth',
                 width=224, height=224):
        with open('human_pose.json', 'r') as f:
            self.human_pose = json.load(f)
        self.topology = trt_pose.coco.coco_category_to_topology(self.human_pose)
        self.model_trt = TRTModule()
        self.model_trt.load_state_dict(torch.load(path_model))
        self.width = width
        self.height = height
        self.parse_objects = ParseObjects(self.topology)

    def __call__(self, frame):
        """
        Gets frame and returns keypoints

        Inputs:
        - frmae: RGB image shaped (self.width, self.height,3)

        Returns:
            keypoints: dictionary where keys are keypoints and values are the x,y coordinates
            list of dictionaries, each element contains dictionary of kepoints per objects
             (keys are keypoints according to self.human_pose and values are the x,y coordinates)
        """

        data = self.preprocess(frame.copy())
        cmap, paf = self.model_trt(data)
        cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
        counts, objects, peaks = self.parse_objects(cmap, paf)
        keypoints = self.get_keypoints(counts, objects, peaks)
        json_pose = self.is_threat(keypoints)
        return json_pose

    def preprocess(self, image):
        """
        Preprocessing of image before entering the network
        """
        mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
        std = torch.Tensor([0.229, 0.224, 0.225]).cuda()
        global device
        device = torch.device('cuda')
        image = cv2.resize(image, (self.width, self.height))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(device)
        image.sub_(mean[:, None, None]).div_(std[:, None, None])
        return image[None, ...]

    def get_keypoints(self, object_counts, objects, normalized_peaks):
        """Get the keypoints from torch data and put into a dictionary where keys are keypoints
        and values the x,y coordinates. The coordinates will be interpreted on the image given.

        Returns:
            dictionary: dictionary where keys are keypoints and values are the x,y coordinates
        """
        count = int(object_counts[0])
        keypoints = []
        for i in range(count):
            obj = objects[0][i]
            C = obj.shape[0]
            dict_keypoints = {}
            for j in range(C):
                k = int(obj[j])
                if k >= 0:
                    peak = normalized_peaks[0][j][k]
                    x = round(float(peak[1]) * self.width)
                    y = round(float(peak[0]) * self.height)
                    dict_keypoints[self.human_pose["keypoints"][j]] = (x, y)
            if len(dict_keypoints) > 1:
                keypoints.append(dict_keypoints)
        return keypoints

    def is_threat(self, keypoints):
        """
        Gets list of dictionaries holding keypoints for each person in the frame and returns list of jsons to tell
        where there are people and are they a threat
        """
        json_pose = []
        for i, person in enumerate(keypoints):
            position = person.get('neck', person[list(person.keys())[0]])
            person_json = {
                'msg': 'detected person',
                'position': position
            }
            json_pose.append(person_json)
        return json_pose