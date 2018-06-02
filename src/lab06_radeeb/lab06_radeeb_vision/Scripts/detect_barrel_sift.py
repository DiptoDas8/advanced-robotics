#! /usr/bin/env python

from __future__ import print_function
from __future__ import division

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Float64

import cv2
from cv_bridge import CvBridge
import time


IMG_WIDTH = 640
FIELD_OF_VIEW = 1.396234
angle_to_barrel_rads = 100


def camera_callback(ros_image):
    start = time.time()
    cam_image = image_converter.imgmsg_to_cv2(ros_image, 'bgr8')
    cam_keypoints, cam_descriptors  =sift.detectAndCompute(cam_image,mask)

    matches = bf_matcher.knnMatch(bar_descriptors,cam_descriptors, k=2)
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
        barrel_x_normalized = barrel_x_location / IMG_WIDTH
        angle_to_barrel_rads = -(barrel_x_normalized - 0.5)* FIELD_OF_VIEW
    else:
        angle_to_barrel_rads = 100
    end = time.time()

    # print(end - start)


def run_bob():
    barrel_publisher = rospy.Publisher('lab06_radeeb/angle_to_barrel_rads', Float64, queue_size=1)
    rate =  rospy.Rate(10)

    while not rospy.is_shutdown():        
        barrel_publisher.publish(angle_to_barrel_rads)
        rate.sleep()

if __name__ == '__main__':

    #Setup CV bridge
    image_converter = CvBridge()

    #Setup SIFT
    bar_image  = cv2.imread('construction_barrel.png', 0)
    sift = cv2.xfeatures2d.SIFT_create()

    mask = None   
    print("1") 
    bar_keypoints, bar_descriptors  = sift.detectAndCompute(bar_image,mask)
    print("2") 
    bf_matcher = cv2.BFMatcher()

    rospy.init_node('bob_barrel_detector', anonymous=True)
    rospy.Subscriber('/lab06_radeeb/camera1/image_raw',Image, camera_callback)

    try:
        run_bob()
    except rospy.ROSInterruptException:
        pass