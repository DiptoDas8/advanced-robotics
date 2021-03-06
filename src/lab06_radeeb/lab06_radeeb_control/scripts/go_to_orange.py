#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

import rospy
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
from std_msgs.msg import String
from geometry_msgs.msg import Twist 
import numpy as np

g_orange_left_frac = 0 
g_orange_right_frac = 0

def frac_callback(orange_frac):
	global g_orange_left_frac, g_orange_right_frac
	g_orange_left_frac = float(orange_frac.data.split(' ')[0])
	g_orange_right_frac = float(orange_frac.data.split(' ')[1])



def run_control_publisher():
	control_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
	
	rate = rospy.Rate(10)
	MAX_ANGULAR_RATE = 1.5
	MAX_LINEAR_RATE = 0.5
	vel_msg = Twist()
	vel_msg.angular.x = 0
	vel_msg.angular.y = 0
	vel_msg.angular.z = 0
	vel_msg.linear.x = 0
	vel_msg.linear.y = 0
	vel_msg.linear.z = 0
	
	while not rospy.is_shutdown():
		#turn in place if we cannot see barrel
		if np.allclose([g_orange_left_frac, g_orange_right_frac], [0.0,0.0]):
			vel_msg.angular.z = MAX_ANGULAR_RATE
			vel_msg.linear.x = 0.0
			print('Turn in place')

		#go straight forward in barrel in middle of view
		elif np.isclose(g_orange_left_frac, g_orange_right_frac):
			vel_msg.angular.z = 0.0 
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('Go Forward')
		
		#veer left
		elif (g_orange_left_frac > g_orange_right_frac):
			vel_msg.angular.z = 0.2* MAX_ANGULAR_RATE 
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('veer left')
		
		#veer right
		else:
			vel_msg.angular.z = -0.2* MAX_ANGULAR_RATE 
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('veer right')

		control_publisher.publish(vel_msg)
		rate.sleep()

if __name__ == '__main__':
	rospy.init_node('orange_frac_controller', anonymous= True)

	rospy.Subscriber('/lab06_radeeb/orange_frac', String, frac_callback)

	try: 
		run_control_publisher()
	except:
		rospy.ROSInterruptException
		pass

