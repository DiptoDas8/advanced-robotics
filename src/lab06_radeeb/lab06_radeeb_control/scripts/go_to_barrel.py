#! /usr/bin/env python

from __future__ import print_function
from __future__ import division

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist

import numpy as np


angular_rads_value = 100

def angular_callback(angluar_data):
    global angular_rads_value
    angular_rads_value = float(angluar_data.data)


def run_control_publisher():
    control_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    rate =  rospy.Rate(10)

    vel_msg = Twist()
    vel_msg.linear.x = 0
    vel_msg.linear.y = 0
    vel_msg.linear.z = 0
    vel_msg.angular.x = 0
    vel_msg.angular.y = 0
    vel_msg.angular.z = 0

    MAX_ANGULAR_RATE =1.5
    MAX_LINEAR_RATE =0.5

    while not rospy.is_shutdown():

        # Go straight forward in barrel in midle of view
        if angular_rads_value == 0:
            vel_msg.angular.z = 0.0
            vel_msg.linear.x = MAX_LINEAR_RATE
            print ('Go forward')

        # Veer Right 
        elif angular_rads_value < 0 :
            vel_msg.angular.z = -0.2 * MAX_ANGULAR_RATE
            vel_msg.linear.x = MAX_LINEAR_RATE
            print ('Veer Right')

        # Veer Left 
        elif angular_rads_value > 0 and angular_rads_value < 1 :
            vel_msg.angular.z = 0.2 * MAX_ANGULAR_RATE
            vel_msg.linear.x = MAX_LINEAR_RATE
            print ('Veer Left')

        # Turn in place if we cannot see cannot see the barrel
        else :
            vel_msg.angular.z = MAX_ANGULAR_RATE
            vel_msg.linear.x = 0.0
            print ('Turn in place')

        control_publisher.publish(vel_msg)
        rate.sleep()



if __name__ == '__main__':
    rospy.init_node('angle_controller',anonymous=True)
    rospy.Subscriber('/lab06_radeeb/angle_to_barrel_rads',Float64, angular_callback)

    try:
        run_control_publisher()
    except rospy.ROSInterruptException:
        pass