FROM node:latest

WORKDIR /frontend
ADD ./package.json ./package.json
ADD ./package-lock.json ./package-lock.json

RUN npm install

ADD . .

CMD ["npm", "run", "serve"]
