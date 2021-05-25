from math import sqrt

import cv2

from object_detector import detect_objects
from pointing_resolver import resolve_pointing_direction


def resolve_target(scene_image, detected_objects, pointing_direction, command_text=None):

    # Gets the gradient and pointing direction from the inputs
    gradient = pointing_direction[0]
    intercept = pointing_direction[1]

    # Detects the first object in the image to be used as the comparison
    first_detected_object = detected_objects[0]
    first_detected_object_name = first_detected_object[0]
    first_detected_object_bounding_box = first_detected_object[1]

    # Gets the bounding box coordinates of the first object detected
    xleft, ytop, xright, ybottom = first_detected_object_bounding_box

    # Calculate midpoint of the bounding box
    mid_x = (xleft + xright) / 2
    mid_y = (ytop + ybottom) / 2

    # Calculates minimum_perpendicular distance from the line of best fit/hand to the first object
    minimum_distance = ((gradient * mid_x + mid_y + intercept) / (sqrt(gradient ** 2 + 1 ** 2)))

    # Sets the target as the first object detected and its bounding box
    target = (first_detected_object_name, first_detected_object_bounding_box)

    # Iterate through all the objects detected to find the closest one to the hand
    for i in range(1, len(detected_objects)):
        detected_object = detected_objects[i]
        detected_object_name = detected_object[0]

        detected_object_bounding_box = detected_object[1]

        xleft, ytop, xright, ybottom = detected_object_bounding_box
        mid_x = (xleft + xright) / 2
        mid_y = (ytop + ybottom) / 2

        distance = ((gradient * mid_x + mid_y + intercept) / (sqrt(gradient ** 2 + 1 ** 2)))

        # If an object is detected to be closer to the line of best fit/hand, set it as the closest object and return its value
        if distance < minimum_distance:
            target = (detected_object_name, detected_object_bounding_box)
            minimum_distance = distance

    # Returns the closest object to the hand/ the object the hand is pointing at
    return target


if __name__ == '__main__':

    for fname in ['scene_image_train/scene_image_07.JPG',
                  'scene_image_train/scene_image_08.JPG',
                  'scene_image_train/scene_image_09.JPG',
                  'scene_image_train/scene_image_10.JPG',
                  'scene_image_train/scene_image_11.JPG',
                  'scene_image_train/scene_image_12.JPG',
                  ]:
        frame = cv2.imread(fname)
        # plt.imshow(frame)
        # plt.show()

        pointing_direction = resolve_pointing_direction(frame)
        print(type(pointing_direction))
        print(f"{fname} : {str(pointing_direction)}")
        objects = detect_objects(frame)
        print(f"{fname} : {str(objects)}")
        target = resolve_target(frame, objects, pointing_direction)
        print(target)

    # Code to allow test run of this component by running 'python target_resolver.py'
    # target = resolve_target(frame, [('laptop', [148, 499, 415, 748]), ('bottle', [547, 446, 622, 640])], [0,1])
    # target = resolve_target(None,[("person",[0,0,100,200]),("person",[0,0,100,100])],[1,0])

    # target = resolve_target(frame, objects, pointing_direction)

    print("ab")
