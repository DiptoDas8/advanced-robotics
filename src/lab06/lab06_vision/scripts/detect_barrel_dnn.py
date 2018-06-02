#!/usr/bin/env python2.7
from __future__ import print_function
from __future__ import division
from subprocess import Popen, PIPE
from os import environ
import time

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2

import numpy as np
import os
# from scipy import misc

image_converter = CvBridge()

prob_BGR_UPPER = np.array((255, 255, 255), dtype='uint8')
prob_BGR_LOWER = np.array((0, 0, 0), dtype='uint8')

g_prob_left_frac = 0
g_prob_right_frac = 0
fastai_env = None
process = None


image_dir = '/home/dipto/ros_workspaces/csc790_labs/src/lab06/lab06_vision/scripts/tmp/'
image_fnames = sorted([])
preds = []

def run(command, env):
    preds = []
    global process
    process = Popen(command, stdin=PIPE, stdout=PIPE,
                    shell=True, bufsize=1, universal_newlines=True,
                    env=env, executable='/bin/bash')

    # for fname in image_fnames:
    #     start_time = time.time()

    #     # Read prompt from fastai_dnn_helper
    #     print('>>', process.stdout.readline().rstrip('\n'))

    #     # Send filename to fastai_dnn_helper
    #     image_fullfile = image_dir + fname
    #     print('Sending:', image_fullfile)
    #     print(image_dir + fname, file=process.stdin)
    #     process.stdin.flush()

    #     # Read response from fastai_dnn_helper
    #     x = process.stdout.readline().rstrip('\n')
    #     # print(x)
    #     print('>>',x)
    #     preds.append(x)
    #     print('Elapsed time:', time.time() - start_time, '\n')

    # # Read final prompt and send quit
    # process.stdout.readline().rstrip('\n')
    # print('quit', file=process.stdin)
    # process.stdin.flush()
    # return preds

def identifier_main():
	global fastai_env
	fastai_env = environ.copy()
	fastai_env['PATH'] = '/home/dipto/anaconda3/bin:' + fastai_env['PATH']
	fastai_env['PYTHONPATH'] = ''
	run('source activate fastai-cpu && /home/dipto/ros_workspaces/csc790_labs/src/lab06/lab06_vision/scripts/fastai_dnn_helper.py', fastai_env)

def communicate(l_img, r_img):
	global process
	preds = []

	start_time = time.time()
	print('>>', process.stdout.readline().rstrip('\n'))
	print('Sending:', l_img)
	print(image_dir + l_img, file=process.stdin)
	process.stdin.flush()

	# Read response from fastai_dnn_helper
	x = process.stdout.readline().rstrip('\n')
	print('>>',x)
	preds.append(x)
	print('Elapsed time:', time.time() - start_time, '\n')

	start_time = time.time()
	print('>>', process.stdout.readline().rstrip('\n'))
	print('Sending:', r_img)
	print(image_dir + r_img, file=process.stdin)
	process.stdin.flush()

	# Read response from fastai_dnn_helper
	x = process.stdout.readline().rstrip('\n')
	print('>>',x)
	preds.append(x)
	print('Elapsed time:', time.time() - start_time, '\n')

	# Read final prompt and send quit
	# process.stdout.readline().rstrip('\n')
	# print('quit', file=process.stdin)
	# process.stdin.flush()
	return preds


def camera_callback(ros_image):
	# rospy.loginfo('got an image')
	# rospy.loginfo('Image is {} by {}'.format(ros_image.width, ros_image.height))
	# rospy.loginfo(ros_image.encoding)

	cv_image = image_converter.imgmsg_to_cv2(ros_image, 'bgr8')

	height, width = cv_image.shape[0], cv_image.shape[1]
	# print(height, width)

	width_cutoff = width//2
	s1 = cv_image[:, :width_cutoff, :]
	s2 = cv_image[:, width_cutoff:, :]

	path = '/home/dipto/ros_workspaces/csc790_labs/src/lab06/lab06_vision/scripts/tmp/'
	# cv2.imwrite(os.path.join(path, 'left_frac_img.png'), s1)
	cv2.imwrite(os.path.join(path, 'left_frac_img.png'), s1)
	cv2.imwrite(os.path.join(path, 'right_frac_img.png'), s2)

	preds = communicate('left_frac_img.png', 'right_frac_img.png')

	# prob_mask = cv2.inRange(cv_image, prob_BGR_LOWER, prob_BGR_UPPER)

	global g_prob_left_frac
	g_prob_left_frac = preds[0]
	# print(g_prob_left_frac)

	
	global g_prob_right_frac
	g_prob_right_frac = preds[1]
	# print(g_prob_right_frac)


	print(g_prob_left_frac, g_prob_right_frac)



	# prob_left = prob_mask[:, 0:int(prob_mask.shape[1]/2)]
	
	# rospy.loginfo('{}', np.sum(prob_left))

	# prob_image = cv2.bitwise_and(cv_image, cv_image, mask = prob_mask)


	# cv2.imshow('prob', np.hstack([cv_image, prob_image]))
	# cv2.waitKey(1)

def init_prob_detector():
	
	rospy.init_node('prob_detector', anonymous=True)

	rospy.Subscriber('/lab06/camera1/image_raw', Image, camera_callback)



	# rospy.spin()

def run_prob_publisher():
	prob_publisher = rospy.Publisher('/lab06/prob_frac', String, queue_size=1)
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		prob_fracs = '{} {}'.format(g_prob_left_frac, g_prob_right_frac)
		prob_publisher.publish(prob_fracs)
		rate.sleep()

if __name__ == '__main__':
	identifier_main()
	init_prob_detector()
	try:
		run_prob_publisher()
	except rospy.ROSInterruptException:
		pass