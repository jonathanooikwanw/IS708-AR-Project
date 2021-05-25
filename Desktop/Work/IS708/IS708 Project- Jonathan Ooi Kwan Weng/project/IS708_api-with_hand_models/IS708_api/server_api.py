import flask
from flask import request
import gesture_segment_picker
import gesture_classifier
import object_detector
import pointing_resolver
import target_resolver
import cv2
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>IS708 API</h1><p>This site is a prototype API for IS708 assignment.</p>"

@app.route('/detect_target', methods=['POST'])
def detect_target():
    """API method 1: detection of target object
    """
    if request.method == 'POST':
        if 'scene_image_file' not in request.files:
            return("image file is not provided")
        else:
            scene_image_file = request.files['scene_image_file']

    command_text = request.form['command_text']

    # Save for debugging
    scene_image_file.save('./temp_scene_image.jpg')
    scene_image = cv2.imread('./temp_scene_image.jpg')
    print(f"Image saved. command_text = {command_text}")

    detected_objects = object_detector.detect_objects(scene_image)
    if detected_objects is None:
        return "No valid objects detected"
    pointing_direction = pointing_resolver.resolve_pointing_direction(scene_image)
    target_object_bounding_box = target_resolver.resolve_target(scene_image, detected_objects, pointing_direction, command_text)

    print(json.dumps(target_object_bounding_box))
    return json.dumps(target_object_bounding_box)


@app.route('/detect_gesture', methods=['POST'])
def detect_gesture():
    """API method 2: detection of provided gesture
    """
    if 'gesture_code' not in request.form:
        return("No gesture provided")
    gesture_code = int(request.form['gesture_code'])
    print(f'Gesture code: {gesture_code}')
    gesture_segment, fname = gesture_segment_picker.pick_gesture_segment(gesture_code)
    gesture_type = gesture_classifier.predict(gesture_segment)

    return json.dumps(gesture_type)

app.run()