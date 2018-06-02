#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2

import numpy as np

image_converter = CvBridge()

ORANGE_BGR_UPPER = np.array((42, 165, 255), dtype='uint8')
ORANGE_BGR_LOWER = np.array((0, 25, 100), dtype='uint8')

g_orange_left_frac = 0
g_orange_right_frac = 0

def camera_callback(ros_image):
	# rospy.loginfo('got an image')
	# rospy.loginfo('Image is {} by {}'.format(ros_image.width, ros_image.height))
	# rospy.loginfo(ros_image.encoding)

	cv_image = image_converter.imgmsg_to_cv2(ros_image, 'bgr8')

	orange_mask = cv2.inRange(cv_image, ORANGE_BGR_LOWER, ORANGE_BGR_UPPER)

	global g_orange_left_frac
	orange_left = orange_mask[:, 0:orange_mask.shape[1]//2]
	orange_left_count = cv2.countNonZero(orange_left)
	g_orange_left_frac = orange_left_count/orange_left.size

	
	global g_orange_right_frac
	orange_right = orange_mask[:, orange_mask.shape[1]//2: ]
	orange_right_count = cv2.countNonZero(orange_right)
	g_orange_right_frac = orange_right_count/orange_right.size


	# print(orange_left_frac, orange_right_frac)



	# orange_left = orange_mask[:, 0:int(orange_mask.shape[1]/2)]
	
	# rospy.loginfo('{}', np.sum(orange_left))

	# orange_image = cv2.bitwise_and(cv_image, cv_image, mask = orange_mask)


	# cv2.imshow('orange', np.hstack([cv_image, orange_image]))
	# cv2.waitKey(1)

def init_orange_detector():
	
	rospy.init_node('orange_detector', anonymous=True)

	rospy.Subscriber('/lab04/camera1/image_raw', Image, camera_callback)



	# rospy.spin()

def run_orange_publisher():
	orange_publisher = rospy.Publisher('/lab04/orange_frac', String, queue_size=1)
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		orange_fracs = '{} {}'.format(g_orange_left_frac, g_orange_right_frac)
		orange_publisher.publish(orange_fracs)
		rate.sleep()

if __name__ == '__main__':
	init_orange_detector()
	try:
		run_orange_publisher()
	except rospy.ROSInterruptException:
		pass