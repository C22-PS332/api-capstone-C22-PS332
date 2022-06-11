# Loading the saved_model
import tensorflow as tf
import six
import time
import numpy as np
import warnings
from PIL import Image
warnings.filterwarnings('ignore')
# from PIL import Image
# from google.colab.patches import cv2_imshow
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from io import BytesIO
# import matplotlib.pyplot as plt
IMAGE_SIZE = (12, 8) # Output display size as you want
PATH_TO_SAVED_MODEL="./saved_model"
print('Loading model...', end='')

# Load saved model and build the detection function
detect_fn=tf.saved_model.load(PATH_TO_SAVED_MODEL)
print('Done!')

#Loading the label_map
category_index=label_map_util.create_category_index_from_labelmap("./label_map.pbtxt",use_display_name=True)
#category_index=label_map_util.create_category_index_from_labelmap([path_to_label_map],use_display_name=True)

def load_image_into_numpy_array(img):

    return np.array(Image.open(BytesIO(img)))

def predictImage(image):
# image_path = "./brok.jpg"
#print('Running inference for {}... '.format(image_path), end='')
# print(image_path)
    image_np = load_image_into_numpy_array(image)

    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image_np)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detect_fn(input_tensor)
    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    image_np_with_detections = image_np.copy()

    def get_classes_name_and_scores(
            boxes,
            classes,
            scores,
            category_index,
            max_boxes_to_draw=20,
            min_score_thresh=.4): # returns bigger than 60% precision
        display_str = []
        if not max_boxes_to_draw:
            max_boxes_to_draw = boxes.shape[0]
        for i in range(min(max_boxes_to_draw, boxes.shape[0])):
            if scores is None or scores[i] > min_score_thresh:
                if classes[i] in six.viewkeys(category_index):
                    if category_index[classes[i]]['name'] not in display_str:
                        display_str.append(category_index[classes[i]]['name'])
                    # display_str.append({
                    #     'name': category_index[classes[i]]['name'],
                    #     'score': '{}%'.format(int(100 * scores[i]))
                    # })
                    # display_str['name'] = category_index[classes[i]]['name']
                    # display_str['score'] = '{}%'.format(int(100 * scores[i]))

        return display_str


    return(get_classes_name_and_scores(
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores'],
        category_index))
