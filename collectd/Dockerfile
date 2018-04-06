# Collectd
FROM resin/raspberrypi3-debian:latest

RUN apt-get update && \
    apt-get install collectd git libpython2.7 python python-smbus && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ttn-collectd

# Python plugins from DBRGN
RUN git clone https://github.com/AmedeeBulle/collectd-python-plugins.git

# Gateway stats plugin
COPY plugins/* collectd-python-plugins/

# Collectd config
COPY collectd.conf /etc/collectd/
COPY collectd.conf.d/* /etc/collectd/collectd.conf.d/

COPY run.sh ./

CMD ["/opt/ttn-collectd/run.sh"]
