import os
import sys
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib, GObject


from pipeline.gresource.gpipeline import GPipeline



# Paths
# input_video = 'input.mp4'
hls_dir = 'hls'
output_playlist = os.path.join('hls/list.m3u8')
print(output_playlist)

# Create HLS directory if it doesn't exist
os.makedirs(hls_dir, exist_ok=True)

# Create index.html
index_html_content ='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HLS Streaming</title>
    <link href="https://vjs.zencdn.net/7.10.2/video-js.css" rel="stylesheet" />
</head>
<body>
    <video-js id="my_video" class="vjs-default-skin" controls preload="auto" width="640" height="360"></video-js>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@1"></script>
<video id="video"></video>
<script>
  var video = document.getElementById('video');
  var videoSrc = 'http://210.206.5.147:5001/hls/0/output.m3u8';
  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(videoSrc);
    hls.attachMedia(video);
  }
  else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = videoSrc;
  }
</script>
<video id="video"></video>
<script>
  var video = document.getElementById('video');
  var videoSrc = 'http://210.206.5.147:5001/hls/1/output.m3u8';
  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(videoSrc);
    hls.attachMedia(video);
  }
  else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = videoSrc;
  }
</script>
<video id="video"></video>
<script>
  var video = document.getElementById('video');
  var videoSrc = 'http://210.206.5.147:5001/hls/2/output.m3u8';
  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(videoSrc);
    hls.attachMedia(video);
  }
  else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = videoSrc;
  }
</script>
<video id="video"></video>
<script>
  var video = document.getElementById('video');
  var videoSrc = 'http://210.206.5.147:5001/hls/3/output.m3u8';
  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(videoSrc);
    hls.attachMedia(video);
  }
  else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = videoSrc;
  }
</script>
</body>
</html>'''

with open(os.path.join(hls_dir, 'index.html'), 'w') as f:
    f.write(index_html_content)


# Serve the HLS content
os.chdir(hls_dir)
server_address = ('', 5001)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
print("Serving HLS on port 5001...")


Gst.init(sys.argv)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)
main_loop = GLib.MainLoop()
gpipeline = GPipeline()
gpipeline.add_bin()
gpipeline.start(main_loop)

pipeline = gpipeline.pipeline
pipeline.set_state(Gst.State.PLAYING)

httpd.serve_forever()
