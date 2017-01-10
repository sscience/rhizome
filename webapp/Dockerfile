FROM node:4.6.0

# https://github.com/b00giZm/docker-compose-nodejs-examples/blob/master/04-express-grunt-watch/Dockerfile

WORKDIR /code

ADD . /code

RUN npm install gulp-cli -g

WORKDIR frontend

RUN npm install

RUN npm rebuild node-sass
