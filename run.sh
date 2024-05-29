docker run -it -d -p 5001:5001 \
  -v ./:/home/infer1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /hls:hls\
  -e DISPLAY=unix$DISPLAY \
  --name testcdn \
  testcdn
