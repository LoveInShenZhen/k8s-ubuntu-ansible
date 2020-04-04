FROM alpine:latest

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk update	&& apk upgrade && apk add keepalived \
    && rm -rf /var/cache/apk/* /tmp/* 

ENTRYPOINT ["/usr/sbin/keepalived", "--dont-fork", "--log-console", "-f", "/etc/keepalived/keepalived.conf"]