FROM node:6

RUN mkdir /watcher-app

RUN npm install gulp-cli -g --silent

WORKDIR /watcher-app

ADD package.json /watcher-app/package.json

RUN npm install
RUN npm cache clean

ADD gulpfile.babel.js /watcher-app/gulpfile.babel.js
ADD . /watcher-app
