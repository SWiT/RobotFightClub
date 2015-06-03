###Robot Fight Club
Copyright (C) 2015 Matthew Gary Switlik

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

###About
Robot Fight Club is an autonomous robot fighting platform. It is built using datamatrices, webcams, Arduinos, Beaglebones, and a Linux PC. The system tracks datamatrix on top of the robot and other objects.  To do this it uses the opencv and dmtx libraries.  The rfcscanner application runs on a Beaglebone Black and scans a video source for the arena edges, if each robot is alive, and its position.  The data is sent over the network to the rfcserver application running on a Linux PC. The rfcserver has a wireless serial connection to each Arduino based robot. Each robot has a balloon that holds down its power button.  When its balloon pops the robot turns off.

The game is simple.  Each robot tries to pop the balloon of the other robots and be the last alive.

We are currently in back in alpha stages.  The old python code didn't scale and was too sensitive for changing lighting conditions. The current Beaglebone Black based solution has one BBB running rfcscanner per 4'x6' arena section.

###You will need:
A PC Running Ubuntu 14.04 or your preferred Linux Distribution.
A webcam capable of 1080p or higher resolution.
A printed set of datamatrices (the arena corners C0-C3 and a two digit number like 00-03).
A Beaglebone Black with 4GB+ of storage (8GB+ Recommended).

###Setup rfcserver (Linux PC)
Install the following packages (Ubuntu):
````
sudo apt-get install git v4l2ucp  git  gcc-avr avr-libc openjdk-7-jre build-essential checkinstall cmake pkg-config yasm libtiff4-dev libjpeg-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev  libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev python-dev python-numpy  libtbb-dev libqt4-dev libgtk2.0-dev libdmtx-utils libdmtx-dev blueman
````

Install the lastest opencv package (3.0+):
```
cd ~
git clone https://github.com/Itseez/opencv.git
cd opencv && mkdir release && cd release
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
make
sudo make install
```

Install the Arduino IDE. http://arduino.cc/en/Main/Software

Give permission for the Arduino IDE to access the serial ports:
```
sudo adduser $USER dialout
```

Download or Clone the RobotKnifeFight code from github:
```
cd ~
git clone https://github.com/SWiT/RobotFightClub.git
cd RobotFightClub
```

Compile rfcserver (optional)
```
g++ -W -Wall rfcserver.cpp -o rfcserver -lopencv_core -lopencv_highgui -lopencv_imgproc
```

Run rfcserver:
```
./rfcserver
```


###Setup rfcscanner (Beaglebone Black)
Download and install the latest Debian image from http://beagleboard.org/latest-images
This guide has been tested with the Debian 4GB 2015-03-01 release.

There are a few things that need to be tweaked once the image is running on a BBB.

Set a password, set the hostname (rfc_bbb#),Set the timezone, and add an alias for 'll',
```
passwd
nano /etc/hostname
sudo dpkg-reconfigure tzdata
echo 'alias ll="ls -la"' >> ~/.bash_aliases
sudo reboot
```

Grow the partition (optional)
```
cd /opt/scripts/tools
git pull
sudo ./grow_partition.sh
sudo reboot
```

Update and install prerequisites.
```
sudo apt-get update && sudo apt-get -y upgrade && sudo apt-get -y dist-upgrade
sudo apt-get -y purge libopencv-dev
sudo rm /usr/lib/libopencv_*
sudo apt-get -y install build-essential cmake pkg-config libtiff4-dev libjpeg-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libdmtx-dev libgtk2.0-dev
sudo reboot
```

Build and Install OpenCV (This takes a few hours)
```
git clone https://github.com/Itseez/opencv.git
cd opencv && mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_CUDA=OFF -D WITH_OPENCL=OFF -D BUILD_opencv_apps=OFF -D BUILD_DOCS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_TESTS=OFF -D ENABLE_NEON=on ..
make
sudo make install
sudo ldconfig
cd ~
```

Build and run rfcscanner
```
git clone https://github.com/SWiT/RobotFightClub.git
cd RobotFightClub
g++ rfcscanner.cpp -o rfcscanner -lopencv_core -lopencv_videoio -lopencv_imgcodecs -ldmtx
./rfcscanner [RFCSERVER_IP]
```
