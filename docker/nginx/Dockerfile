FROM nginx

RUN apt-get update && \
    apt-get -y install nodejs npm
RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN npm install webpack@1.12.15 -g

RUN mkdir /themyarchive
WORKDIR /themyarchive
RUN mkdir /themyarchive/themyarchive
ADD package.json /themyarchive/package.json
RUN NODE_ENV=production npm install

ADD themyarchive/static /themyarchive/themyarchive/static
ADD webpack.config.js /themyarchive/webpack.config.js
RUN NODE_ENV=production webpack

COPY docker/nginx/default.conf /etc/nginx/conf.d/
