FROM node:latest

LABEL authors="pgdev"

WORKDIR /srv/app/

ENV PATH /srv/app/node_modules/.bin:$PATH

COPY package.json .
COPY package-lock.json .
RUN npm install --legacy-peer-deps

COPY . .
