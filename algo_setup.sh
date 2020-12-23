#!/bin/bash

# installing torch
wget https://nvidia.box.com/shared/static/wa34qwrwtk9njtyarwt5nvo6imenfy26.whl -O torch-1.7.0-cp36-cp36m-linux_aarch64.whl
apt-get install libopenblas-base libopenmpi-dev
pip3 install Cython
pip3 install torch-1.7.0-cp36-cp36m-linux_aarch64.whl

# installing torchvision
apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev
git clone --branch v0.8.1 https://github.com/pytorch/vision torchvision
cd torchvision
export BUILD_VERSION=0.8.1
python3 setup.py install
cd ../

# installing torch2trt
git clone https://github.com/NVIDIA-AI-IOT/torch2trt
cd torch2trt
python3 setup.py install --plugins

pip3 install tqdm pycocotools
apt-get install python3-matplotlib
cd ../

# installing trt_pose
git clone https://github.com/NVIDIA-AI-IOT/trt_pose
cd trt_pose
python3 setup.py install