FROM node:latest

WORKDIR /frontend
ADD ./package.json ./package.json
ADD ./package-lock.json ./package-lock.json

RUN npm install
RUN export PATH="./node_modules/.bin:$PATH"

ADD . .

CMD ["npm", "run", "serve"]
