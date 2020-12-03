## Setting up:
For video source, you have two options:
 - Robomaster:
 -  Camera:
In both options, the device must be connected to the jetson via usb port.
Accessing the rest-API for information is through ethernet connection - 'eth0'
## Running the project:
- load image moshe:v0.1
from the project folder:
- build image using the command:
> docker build -t moshe:v0.2 . 
- run the docker with the appropriate environment variable using:
> docker run -it --network=host -e STREAM_KIND=$$$ moshe:v0.2
Where STREAM_KIND can be one of two options:
1. ROBOT - using robomaster camera
2. CAMERA - using camera connected to the jetson