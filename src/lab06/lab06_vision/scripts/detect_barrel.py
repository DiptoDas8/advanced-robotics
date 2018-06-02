#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String, Float64

import cv2
from cv_bridge import CvBridge


IMAGE_WIDTH = 640
FIELD_OF_VIEW = 1.396234
angle_to_barrel_rads = 100


def camera_callback(ros_image):
    """Detect the color orange.

    rosmsg show sensor_msgs/Image
        std_msgs/Header header
          uint32 seq
          time stamp
          string frame_id
        uint32 height
        uint32 width
        string encoding
        uint8 is_bigendian
        uint32 step
        uint8[] data

    For /lab06/camera1/image_raw
        height       = 480
        width        = 640
        encoding     = rgb8
        is_bigendian = false
        step         = 1920 (width * 3 = 640 * 3)
        data         = length is 921600 (step * height = 1920 * 480)
    """

    cam_image = image_converter.imgmsg_to_cv2(ros_image, 'bgr8')
    cam_image = cv2.cvtColor(cam_image, cv2.COLOR_BGR2GRAY)
    cam_keypoints, cam_descriptors = sift.detectAndCompute(cam_image, mask)

    matches = bf_matcher.knnMatch(bar_descriptors, cam_descriptors, k=2)

    good_matches = [[m] for m, n in matches if m.distance < 0.8 * n.distance]

    global angle_to_barrel_rads

    num_matches = len(good_matches)
    if num_matches > 0:
        barrel_x_location = 0
        for match in good_matches:
            keypoint_index = match[0].trainIdx
            keypoint_x_location = cam_keypoints[keypoint_index].pt[0]
            barrel_x_location += keypoint_x_location
        barrel_x_location /= num_matches
        barrel_x_normalized = barrel_x_location / IMAGE_WIDTH

        angle_to_barrel_rads = -(barrel_x_normalized - 0.5) * FIELD_OF_VIEW
    else:
        angle_to_barrel_rads = 100


def run_bob():

    barrel_publisher = rospy.Publisher('/lab06/angle_to_barrel_rads', Float64, queue_size=1)
    # barrel_publisher = rospy.Publisher('/lab06/angle_to_barrel_rads', String, queue_size=1)


    rate = rospy.Rate(10)

    while not rospy.is_shutdown():

        barrel_publisher.publish(angle_to_barrel_rads)

        rate.sleep()


if __name__ == '__main__':

    # Setup cv bridge
    image_converter = CvBridge()

    # Setup SIFT
    bar_image = cv2.imread('barrel_only.png', 0)
    sift = cv2.xfeatures2d.SIFT_create()

    mask = None
    print(bar_image.shape)
    # bar_image = cv2.cvtColor(bar_image, cv2.COLOR_BGR2GRAY)	# passing 0 as the second argument makes the image grayscale by default
    bar_keypoints, bar_descriptors = sift.detectAndCompute(bar_image, mask)

    bf_matcher = cv2.BFMatcher()


    rospy.init_node('bob_the_barrel_detector', anonymous=True)

    rospy.Subscriber('/lab06/camera1/image_raw', Image, camera_callback)

    try:
        run_bob()
    except rospy.ROSInterruptException:
        pass
