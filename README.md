Robot Fight Club Arena v0.11 (master)

Robot Fight Club Arena is a platform built using Python 2.7+, Arduino v1.5.6-r2 BETA, OpenCV 2.4.9+, and dmtx 0.7.4.  It scans video sources for data matrices and status LEDs to determine the arena edges, if each robot is alive, and its position.  The data is sent out via serial radios to each Arduino robot.  Each robot has a balloon that holds down its power button.  When its balloon pops the robot turns off.

The game is simple.  Each robot tries to pop the balloon of the other robots and be the last alive.

We are currently in Beta stages.  Positioning works but could use optimizations.  

This guide will walk you through setting up an arena for Robot Fight Club.

You will need:
    a PC Running Ubuntu 14.04 or your preferred Linux Distribution.
    a webcam capable of 1080p or higher resolution.
    the printed datamatrices

Install the following packages (Ubuntu):
    sudo apt-get install git v4l2ucp  git  gcc-avr avr-libc openjdk-7-jre build-essential checkinstall cmake pkg-config yasm libtiff4-dev libjpeg-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev  libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev python-dev python-numpy  libtbb-dev libqt4-dev libgtk2.0-dev libdmtx-utils libdmtx-dev blueman

Install pydmtx:
    cd ~
    git clone https://github.com/dmtx/dmtx-wrappers.git
    cd dmtx-wrappers/python
    sudo python setup.py install

Install the lastest opencv package (2.4.9+):
    cd ~
    git clone https://github.com/Itseez/opencv.git
    cd opencv
    git checkout -b 2.4 origin/2.4
    mkdir release
    cd release
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
    make
    sudo make install

Install Arduino 1.5.6-r2 BETA or later:
    http://arduino.cc/en/Main/Software

Give permission for the Arduino IDE to access the serial ports:
    sudo adduser $USER dialout

Download or Clone the RobotKnifeFight code from github:
    cd ~
    git clone git@github.com:SWiT/RobotFightClubArena.git

Run the Arena server:
    cd RobotKnifeFight
    python rfcarena.py
