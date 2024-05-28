import os
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

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
    <script src="https://vjs.zencdn.net/7.10.2/video.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/videojs-contrib-hls/5.14.1/videojs-contrib-hls.js"></script>
    <script>
        var player = videojs('my_video');
        player.src({
            src: 'list.m3u8',
            type: 'application/x-mpegURL'
        });
    </script>
</body>
</html>'''

with open(os.path.join(hls_dir, 'index.html'), 'w') as f:
    f.write(index_html_content)

# Serve the HLS content
os.chdir(hls_dir)
server_address = ('', 8000)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
print("Serving HLS on port 8000...")
httpd.serve_forever()
