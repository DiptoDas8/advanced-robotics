#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

from subprocess import Popen, PIPE
from os import environ

import rospy
from sensor_msgs.msg import Image
import sys

import cv2
from cv_bridge import CvBridge

from geometry_msgs.msg import Twist

def camera_callback(ros_image):  
  cam_image = image_converter.imgmsg_to_cv2(ros_image, 'bgr8')
  cv2.imwrite('cam_img.png', cam_image)


def run(command, env):
  process = Popen(command, stdout=PIPE, shell=True, env=env, executable='/bin/bash')
  control_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

  rate = rospy.Rate(10)

  vel_msg= Twist()
  vel_msg.linear.x=0.0
  vel_msg.linear.y=0
  vel_msg.linear.z=0
  vel_msg.angular.x=0
  vel_msg.angular.y=0
  vel_msg.angular.z=0.0
  
  MAX_ANGULAR_RATE =0.5
  MAX_LINEAR_RATE =0.8

  while not rospy.is_shutdown():    
    x = process.stdout.readline().rstrip('\n')    
    print(x)      
    
    if len(x) > 15:
      yprobability = float(x[2:6])
      nprobability = float(x[10:15])

      # Turn in place if we cannot see cannot see the barrel      
      if yprobability < 0.8 and nprobability < 0.8:
        vel_msg.angular.z = -MAX_ANGULAR_RATE
        vel_msg.linear.x = 0.0
        print ('Turn in place')      

      # Go straight forward in barrel in midle of view
      else :
        vel_msg.angular.z = 0.0
        vel_msg.linear.x = MAX_LINEAR_RATE
        print ('Go forward')
    
    control_publisher.publish(vel_msg)
    rate.sleep()



if __name__ == '__main__':
  fastai_env = environ.copy()
  fastai_env['PATH'] = '/home/dipto/anaconda3/bin:' + fastai_env['PATH']
  fastai_env['PYTHONPATH'] = ''

  rospy.init_node('Driver', anonymous=True)
  rospy.Subscriber('/lab06_radeeb/camera1/image_raw', Image, camera_callback,queue_size=1)

  image_converter=CvBridge()

  run('source activate fastai-cpu && /home/dipto/ros_workspaces/csc790_labs/src/lab06_radeeb/lab06_radeeb_vision/Scripts/fastai_helper.py', fastai_env)
