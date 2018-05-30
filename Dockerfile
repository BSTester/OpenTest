FROM centos/python-35-centos7
USER root
VOLUME /data
WORKDIR /data
COPY ./ /data
RUN /bin/bash -c 'cd /data && pip install --upgrade pip && pip install -r /data/requirements.txt && \
	yum -y install epel-release && \
	yum -y install nodejs && \
	npm install -g cnpm --registry=https://registry.npm.taobao.org && \
	cnpm install --global --no-optional phantomas phantomjs-prebuilt && \
	yum -y groupinstall fonts && \
	ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime'
EXPOSE 9090
CMD /bin/bash -c 'python /data/app_server.py --monitor=on --port=9090 --log_file_prefix=/data/logs/openTest.log --log-file-max-size=10000000 --log-file-num-backups=3'