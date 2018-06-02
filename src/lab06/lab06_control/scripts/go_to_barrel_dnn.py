#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist

import numpy as np

g_prob_left_frac = 0
g_prob_right_frac = 0


def frac_callback(prob_frac):
	global g_prob_left_frac, g_prob_right_frac
	g_prob_left_frac = float(prob_frac.data.split(' ')[0])
	g_prob_right_frac = float(prob_frac.data.split(' ')[1])

	print(g_prob_left_frac, g_prob_right_frac)

def run_control_publisher():
	control_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
	rate = rospy.Rate(10)
	vel_msg = Twist()
	vel_msg.angular.x = 0.0
	vel_msg.angular.y = 0.0
	vel_msg.angular.z = 0.0
	vel_msg.linear.x = 0.0
	vel_msg.linear.y = 0.0
	vel_msg.linear.z = 0.0
	

	MAX_ANGULAR_RATE = 0.1
	MAX_LINEAR_RATE = 0.5
	while not rospy.is_shutdown():
		# prob_fracs = '{} {}'.format(g_prob_left_frac, g_prob_right_frac)
		# write code here
		if np.allclose([g_prob_left_frac, g_prob_right_frac], [0.0, 0.0]):
			vel_msg.angular.z = MAX_ANGULAR_RATE
			vel_msg.linear.x = 0.0
			print('Turn in place')
		elif np.allclose([g_prob_left_frac, g_prob_right_frac], [1.0, 1.0]):
			vel_msg.angular.z = 0.0
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('Go forward')
		elif g_prob_left_frac>g_prob_right_frac:
			# go left
			vel_msg.angular.z = 0.2*MAX_ANGULAR_RATE
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('Go left')
		elif g_prob_right_frac>g_prob_left_frac:
			# go right
			vel_msg.angular.z = -0.2*MAX_ANGULAR_RATE
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('Go right')
		else:
			# go straight
			print('is it really a must?')
		control_publisher.publish(vel_msg)
		rate.sleep()


if __name__ == '__main__':
	rospy.init_node('prob_frac_controller', anonymous=True)
	rospy.Subscriber('/lab06/prob_frac', String, frac_callback)
	# rospy.spin()
	try:
		run_control_publisher()
	except rospy.ROSInterruptException:
		pass