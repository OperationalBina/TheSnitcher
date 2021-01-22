import torch
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

from detectron2.structures.instances import Instances


class PoseEstimator:
    def __init__(self,
                 model_yml: str = "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml",
                 threshold: float = 0.7):
        """
        assuming all images send to class methods are in a BGR format (i.e. opened using cv2)

        Args:
            model_yml: path to yaml files that define what model to take
            threshold: dection threshold, a number in [0, 1] range
        """
        self.cfg = get_cfg()  # get a fresh new config
        self.cfg.MODEL.DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.cfg.merge_from_file(model_zoo.get_config_file(model_yml))
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = threshold  # set threshold for this model
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(model_yml)
        self.predictor = DefaultPredictor(self.cfg)

    def get_full_prediction(self, image) -> Instances:
        """
        get a full prediction of the image, including:
            - pred_boxes
            - scores
            - pred_keypoints
            - pred_keypoint_heatmaps
        Args:
            image:

        Returns:

        """
        outputs = self.predictor(image)

        return outputs['instances']

    def get_key_points(self, image):
        """
        return just the key points
        Args:
            image:

        Returns: a tensor of shape [#instances, #key_points, 3]. 3 = (x, y, visibility)

        """
        return self.get_full_prediction(image).pred_keypoints

    def draw_prediction_on_image(self, image, predictions, ax=None):
        """
        draws the prediction on the image

        Args:
            image:
            predictions: the output of the get_full_prediction method
            ax: a matplotlib axis, if given plots on it

        Returns: the image with the prediction drawn on it in a RGB format

        """
        v = Visualizer(image[:, :, ::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]))
        drawn_img = v.draw_instance_predictions(predictions.to("cpu")).get_image()

        if ax is not None:
            ax.imshow(drawn_img)
            ax.axis('off')

        return drawn_img
