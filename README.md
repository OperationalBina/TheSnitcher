## Setting up:
For video source, you have two options:
 - Robomaster:
 -  Camera:

In both options, the device must be connected to the jetson via usb port.

Accessing the rest-API for information is through ethernet connection - 'eth0'

## Running the project:
- build image from the project folder using the command:
> docker build -t snitcher . 
- run the docker with the appropriate environment variable using:
> docker run -it --network=host -e STREAM_KIND=$$$ snitcher

Where STREAM_KIND can be one of two options:

- ROBOT - using robomaster camera
- CAMERA - using camera connected to the jetson

For support, open an issue.

