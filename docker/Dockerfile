FROM centos:7
MAINTAINER dvrcic@srce.hr
RUN groupadd user -g 1000 && useradd -u 1000 -g 1000 user -m -d /home/user -s /bin/zsh
RUN yum -y update; yum clean all
RUN yum -y install epel-release && \
    yum -y install \
      ack \
      ctags \
      fortune-mod \
      git \
      iproute \
      make \
      mc \
      net-tools \
      python-devel \
      python-pip \
      python-setuptools \
      python3-devel \
      python3-setuptools \
      rpmdevtools \
      sshd \
      sudo \
      the_silver_searcher \
      tmux \
      vim \
      wget \
      yum-utils \
      zsh
RUN pip install -U pip; pip3 install -U pip
RUN pip2 install wheel ipdb setuptools; pip3 install -U wheel ipdb setuptools
RUN passwd -d root
VOLUME [ "/sys/fs/cgroup" ]
RUN echo "user ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers
COPY tmux-2.9a-3.el7.x86_64.rpm ./
RUN yum localinstall -y tmux-2.9a-3.el7.x86_64.rpm
USER user
WORKDIR /home/user
RUN curl -sfL https://git.io/chezmoi | sh
CMD ["/bin/zsh"]
