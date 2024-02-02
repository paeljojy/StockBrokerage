# FROM ubuntu:latest 

FROM node:21

RUN \
    apt-get update && \
    apt-get upgrade 
    # && \
    # echo "cwd is: '$(pwd)'" &&\
    # apt install openssl && \
    # useradd -m -s /bin/bash -G sudo -p $(openssl passwd -1 "password") stock && \
    # cd /home/stock && \
    # echo "stock home is: '$(pwd)'"
    # apt-get install npm \
    # apt-get install nodejs \
    # apt-get install git
    # apt get install sqlite3
    # cd $HOME \
    # git clone --recursive git@github.com:paeljojy/StockBrokerage.git

# Build stage
FROM node:21 as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# RUN npm run build

# Production stage
# FROM nginx:1.17.1-alpine as production-stage
# RUN rm -rf /etc/nginx/conf.d
# COPY conf /etc/nginx
# COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
EXPOSE 5173
# CMD ["nginx", "-g", "daemon off;"]
CMD ["npm", "run", "dev", "--host"]

