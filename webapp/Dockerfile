FROM node:4.3.2

RUN mkdir /watcher-app
RUN mkdir /code

RUN npm install gulp-cli -g

WORKDIR /watcher-app

ADD package.json /watcher-app/package.json
ADD external /watcher-app/external

RUN npm install

ADD gulpfile.babel.js /watcher-app/gulpfile.babel.js
ADD . /watcher-app
