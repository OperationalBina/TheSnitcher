FROM registry.hub.docker.com/mdegans/deepstream:aarch64-samples

COPY . .

RUN apt update
RUN apt install -y --fix-missing python3-pip
RUN pip3 install --upgrade pip
RUN pip install --timeout=6000 opencv-python

RUN pip3 install -r requirements.txt 
RUN apt-get -y install libopus-dev libavcodec-dev libswscale-dev 
RUN apt-get -y install cmake 
RUN cd ./src/stream/decoder \
    && chmod +x build.sh \ 
    && ./build.sh
RUN chmod +777 start_rob.sh
ENTRYPOINT ["./start_rob.sh"] 

