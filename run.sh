docker run -d -p 5000:5000
  -v $(pwd):/home/infer1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=unix$DISPLAY \
  --name testcdn

docker exec -it testcdn bash