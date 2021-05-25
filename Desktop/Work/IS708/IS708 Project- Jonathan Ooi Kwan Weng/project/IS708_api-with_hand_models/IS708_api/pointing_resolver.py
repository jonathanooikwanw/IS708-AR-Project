'''
@author: gprana
'''
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np


# Returns line of pointing direction
def resolve_pointing_direction(scene_image):
    """Given scene image containing a pointing right hand, this function returns the line of pointing direction
    Argument:
    scene_image -- binary data of scene image containing pointing hand
    Return value:
    List containing coordinates representing a line corresponding to pointing direction 
    of the hand in the scene image
    """
    protoFile = "hand/pose_deploy.prototxt"
    weightsFile = "hand/pose_iter_102000.caffemodel"
    nPoints = 22

    # frame = cv2.imread("hand.jpg")

    frameCopy = np.copy(scene_image)
    frameWidth = scene_image.shape[1]
    frameHeight = scene_image.shape[0]
    aspect_ratio = frameWidth / frameHeight
    threshold = 0.1

    t = time.time()
    # input image dimensions for the network
    inHeight = 736
    # inWidth = 368
    inWidth = int(((aspect_ratio * inHeight) * 8) // 8)
    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

    inpBlob = cv2.dnn.blobFromImage(frameCopy, 1.0 / 255, (inWidth, inHeight),
                                    (0, 0, 0), swapRB=False, crop=False)

    net.setInput(inpBlob)

    output = net.forward()
    # print("time taken by network : {:.3f}".format(time.time() - t))

    # Empty list to store the detected keypoints
    points = []

    for i in range(nPoints):
        # confidence map of corresponding body's part.
        probMap = output[0, i, :, :]
        probMap = cv2.resize(probMap, (frameWidth, frameHeight))

        # Find global maxima of the probMap.
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

        if prob > threshold:
            cv2.circle(frameCopy, (int(point[0]), int(point[1])), 3, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frameCopy, "{}".format(i), (int(point[0]), int(point[1])), cv2.FONT_HERSHEY_SIMPLEX, .8,
                        (0, 0, 255), 2, lineType=cv2.LINE_AA)

            # Add the point to the list if the probability is greater than the threshold
            points.append([int(point[0]), int(point[1])])
        else:
            points.append(None)
    cv2.imwrite("test.jpg", frameCopy)

    # Line of best fit calculation
    total_x, total_y = 0, 0

    # remove the None types in the list
    points2 = [elem for elem in points if elem is not None]
    rows = len(points2)

    # Finding the total x values and y values and obtaining the mean of them.
    for i in range(rows):
        x = points2[i][0]
        total_x = total_x + x

    for i in range(rows):
        y = points2[i][1]
        total_y = total_y + y

    mean_x = total_x / rows
    mean_y = total_y / rows

    total = 0
    totalX2 = 0

    # Calculating the gradient and y-intercept of the line of best fit
    for i in range(rows):
        x = points2[i][0]
        y = points2[i][1]
        total = total + ((x - mean_x) * (y - mean_y))
        totalX2 = totalX2 + ((x - mean_x) ** 2)

    gradient = total / totalX2
    intercept = mean_y - (gradient * mean_x)

    return [gradient, intercept]


if __name__ == '__main__':
    # Code to allow test run of this component by running 'python pointing_resolver.py'
    for fname in ['scene_image_train/scene_image_07.JPG',
                  'scene_image_train/scene_image_08.JPG',
                  'scene_image_train/scene_image_09.JPG',
                  'scene_image_train/scene_image_10.JPG',
                  'scene_image_train/scene_image_11.JPG',
                  'scene_image_train/scene_image_12.JPG',
                  ]:
        try:
            frame = cv2.imread(fname)
            output = resolve_pointing_direction(frame)
            gradient = output[0]
            intercept = output[1]
            print("Gradient: " + str(gradient), "Intercept: " + str(intercept))
            plt.axline((0, intercept), slope=gradient, color="black", linestyle=(0, (5, 5)))
            imgplot = plt.imshow(frame)
            plt.show()
            # output = resolve_pointing_direction(frame)
            # print(f"{fname} : {str(output)}")
        except Exception as e:
            print(e)
            print(f"Unable to detect pointing direction for {fname}")
