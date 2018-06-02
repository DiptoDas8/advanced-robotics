#!/usr/bin/env sh

# First program argument is an x-axis linear speed

LIN_SPEED="0.1"
if [ ! -z "$1" ]; then
    LIN_SPEED=$1
fi

# Second program argument is an z-axis angular speed

ANG_SPEED="0.0"
if [ ! -z "$2" ]; then
    ANG_SPEED=$2
fi

rostopic pub -1 /cmd_vel geometry_msgs/Twist "{\
    linear:  {x: $LIN_SPEED, y: 0.0, z: 0.0},\
    angular: {x: 0.0,        y: 0.0, z: $ANG_SPEED}}"
