FROM nvcr.io/nvidia/tensorrt:22.12-py3

ENV NAME=infer1
ENV NVIDIA_DRIVER_CAPABILITIES=all

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} >/etc/timezone

RUN apt update && apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y --allow-unauthenticated \
    sudo openssh-server vim nano ssh ccache curl wget tmux unzip tar zsh \
    pkg-config tzdata ca-certificates \
    build-essential gnupg gnupg-agent \
    libssl-dev libffi-dev libgl1-mesa-glx
RUN dpkg-reconfigure -f noninteractive tzdata

RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list
RUN apt update && apt upgrade -y
RUN apt autoremove -y
RUN rm -rf /var/lib/apt/lists/*
RUN rm -rf /var/cache/apt/archives/*
RUN apt-get install libffi6

RUN apt-get update -y
RUN apt-get install -y python3-dev python3-pip
RUN apt-get update -y

RUN apt-get install -y cmake iputils-ping libcairo2-dev libgtk-3-dev libxt-dev libgirepository1.0-dev
RUN apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x
RUN apt-get install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    libgstreamer-plugins-base1.0-dev gstreamer1.0-libav gir1.2-gst-rtsp-server-1.0 gstreamer1.0-tools python3-gi-cairo
RUN apt-get update -y

RUN pip install nvitop debugpy pycairo PyMySQL cryptography zmq pika python-dotenv

RUN useradd -rm -d /home/${NAME} -s /bin/bash -g root -G \
    sudo -u 1000 ${NAME}
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >>/etc/sudoers
RUN chsh -s /bin/bash

USER ${NAME}
WORKDIR /home/${NAME}

EXPOSE 6003

ENTRYPOINT ["/bin/bash" ]
CMD ["-c", "pip install -r requirements.txt && \
            /bin/bash "]

