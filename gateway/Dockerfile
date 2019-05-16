# Build as non-resin for now
# FROM resin/%%RESIN_MACHINE_NAME%%-debian:stretch AS buildstep
FROM resin/raspberrypi3-debian:stretch AS buildstep

WORKDIR /opt/ttn-gateway/

# downloading utils
RUN apt-get update && \
    apt-get install wget build-essential libc6-dev git pkg-config protobuf-compiler libprotobuf-dev libprotoc-dev automake libtool autoconf python-dev python-rpi.gpio

COPY dev dev
RUN ./dev/build.sh

# FROM resin/%%RESIN_MACHINE_NAME%%-debian:stretch
FROM resin/raspberrypi3-debian:stretch

WORKDIR /opt/ttn-gateway

RUN apt-get update && \
    apt-get install python-rpi.gpio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=buildstep /opt/ttn-gateway/mp_pkt_fwd .
COPY --from=buildstep /usr/local/lib/libpaho-embed-* /usr/lib/
COPY --from=buildstep /usr/lib/libttn* /usr/lib/

COPY run.py ./

WORKDIR /var/ttn

CMD ["/opt/ttn-gateway/run.py"]
