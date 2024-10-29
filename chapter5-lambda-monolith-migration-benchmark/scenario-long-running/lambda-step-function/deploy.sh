#!/bin/bash

# Prepare the files to be used by the lambda layer
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xvf ffmpeg-release-amd64-static.tar.xz
mkdir -p ffmpeg/bin
cp ffmpeg-7.0.2-amd64-static/ffmpeg ffmpeg/bin/
cd ffmpeg
zip -r ../ffmpeg.zip .
cd ..
aws s3 cp ffmpeg.zip s3://tesina-casaburi-ffmpeg/

# Deploy the stack
sam build && sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
