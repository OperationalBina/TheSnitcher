FROM moshe:v0.3

COPY . .

RUN pip3 install -r requirements.txt 
RUN apt-get -y install libopus-dev libavcodec-dev libswscale-dev 
RUN apt-get -y install cmake 
RUN cd ./src/stream/decoder \
    && chmod +x build.sh \ 
    && ./build.sh
RUN chmod +777 start_rob.sh
ENTRYPOINT ["./start_rob.sh"] 

