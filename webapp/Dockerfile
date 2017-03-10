FROM mhart/alpine-node:4.7.2

RUN mkdir /watcher-app
RUN mkdir /code

RUN apk add --no-cache make gcc g++ python

RUN npm install gulp-cli -g --silent

WORKDIR /watcher-app

ADD package.json /watcher-app/package.json
ADD external /watcher-app/external

RUN npm install
RUN npm cache clean

ADD gulpfile.babel.js /watcher-app/gulpfile.babel.js
ADD . /watcher-app
