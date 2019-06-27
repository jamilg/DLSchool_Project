import os
import base64
import numpy as np
import six.moves.urllib as urllib
import sys
import tensorflow as tf
from collections import defaultdict
from io import StringIO, BytesIO
from PIL import Image
sys.path.append("..")
from app.utils import label_map_util
from app.utils import visualization_utils as vis_util
MODEL_NAME = 'app/ssd_mobilenet_v1_coco_2018_01_28'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('app/data', 'mscoco_label_map.pbtxt')
NUM_CLASSES = 90
UPLOAD_FOLDER = 'app/static/uploads'


class ObjectDetector():
    def __init__(self):
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
          od_graph_def = tf.compat.v1.GraphDef()
          with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

    def load_image_into_numpy_array(self, image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

    def encode_image(self, image):
        image_buffer = BytesIO()
        image.save(image_buffer, format='PNG')
        mime_str = 'data:image/png;base64,'
        imgstr = '{0!s}'.format(base64.b64encode(image_buffer.getvalue()))
        quote_index = imgstr.find("b'")
        end_quote_index = imgstr.find("'", quote_index+2)
        imgstr = imgstr[quote_index+2:end_quote_index]
        imgstr = mime_str + imgstr
        return imgstr

    def detect(self, filename):
        IMAGE_PATH = UPLOAD_FOLDER + "/" + filename

        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                image = Image.open(IMAGE_PATH)
                image_np = self.load_image_into_numpy_array(image)
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    self.category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8)
                im = Image.fromarray(image_np)
                imgsrc = self.encode_image(im.copy())
                im.save(UPLOAD_FOLDER + "/"+ filename)
        return imgsrc