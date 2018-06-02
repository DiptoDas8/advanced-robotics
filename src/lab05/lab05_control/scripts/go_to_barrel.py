#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

import rospy
from std_msgs.msg import String, Float64
from geometry_msgs.msg import Twist

import numpy as np

angle_to_barrel = 0

def angle_callback(angle_to_barrel_rads):
	global angle_to_barrel
	# print(type(angle_to_barrel_rads))
	angle_to_barrel = float(angle_to_barrel_rads.data)
	print(angle_to_barrel)

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
	

	MAX_ANGULAR_RATE = 0.5
	MAX_LINEAR_RATE = 0.5
	while not rospy.is_shutdown():
		if np.isclose(angle_to_barrel, 100.0):		#np.isclose(angle_to_barrel, 100.0)
			vel_msg.angular.z = MAX_ANGULAR_RATE
			vel_msg.linear.x = 0.0
			print('Turn in place')
		elif np.isclose(angle_to_barrel, 0.0):	#np.isclose(angle_to_barrel, 0.0)
			vel_msg.angular.z = 0.0
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('Go forward')
		elif angle_to_barrel>0.0:
			# go left
			vel_msg.angular.z = 0.2*MAX_ANGULAR_RATE
			vel_msg.linear.x = MAX_LINEAR_RATE
			print('Go left')
		elif angle_to_barrel<0.0:
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
	rospy.init_node('towards_barrel_controller', anonymous=True)
	rospy.Subscriber('/lab05/angle_to_barrel_rads', Float64, angle_callback)
	# rospy.Subscriber('/lab05/angle_to_barrel_rads', String, angle_callback)
	
	# rospy.spin()
	try:
		run_control_publisher()
	except rospy.ROSInterruptException:
		pass