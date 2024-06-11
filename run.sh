docker run --gpus all -it -d -p 6003:6003 \
  -v ./:/home/infer1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /hls:/home/infer1/hls\
  -e DISPLAY=unix$DISPLAY \
  --name testcdn \
  testcdn
