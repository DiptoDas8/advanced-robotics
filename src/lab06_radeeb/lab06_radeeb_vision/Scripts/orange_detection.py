#!/usr/bin/env python

from __future__ import print_function
from __future__ import division


import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String

import cv2
import numpy as np


image_converter = CvBridge()

#upper bound and lower bounds of orange
ORANGE_LOWER_BOUND =  np.array((0, 25, 100), dtype='uint8')
ORANGE_UPPER_BOUND = np.array((42, 165, 255), dtype='uint8')

g_orange_left_frac = 0
g_orange_right_frac = 0

def camera_callback(ros_image):
	cv_image = image_converter.imgmsg_to_cv2(ros_image, "bgr8")
	orange_mask = cv2.inRange(cv_image, ORANGE_LOWER_BOUND, ORANGE_UPPER_BOUND)

	global g_orange_left_frac
	orange_left = orange_mask[:, 0: int(orange_mask.shape[1]//2)]
	orange_left_count = cv2.countNonZero(orange_left)
	g_orange_left_frac = orange_left_count / orange_left.size
	
	global g_orange_right_frac
	orange_right = orange_mask[:, int(orange_mask.shape[1]//2):]
	orange_right_count = cv2.countNonZero(orange_right)
	g_orange_right_frac = orange_right_count / orange_right.size

	orange_image = cv2.bitwise_and(cv_image, cv_image, mask=orange_mask)
	cv2.imshow('orange', np.hstack([cv_image, orange_image]))
	cv2.waitKey(1)

def orange_detector():
	rospy.init_node('orange_detector', anonymous= True)

	rospy.Subscriber('/lab06_radeeb/camera1/image_raw', Image, camera_callback)

	#rospy.spin() #keeps messaging open

	

def run_orange_publisher():
	orange_publisher = rospy.Publisher('/lab06_radeeb/orange_frac', String, queue_size=1)
	rate = rospy.Rate(10)

	while not rospy.is_shutdown():
		orange_fracs= '{} {}'.format(g_orange_left_frac, g_orange_right_frac)
		orange_publisher.publish(orange_fracs)
		rate.sleep()
 
if (__name__) == '__main__':
	orange_detector()

	try:
		run_orange_publisher()
	except rospy.ROSInterruptException:
		pass

