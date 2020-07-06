#!/bin/bash
app="api"
docker build -t ${app} .
docker run -p 5000:5000 \
  --name=${app} \
  -v $PWD:/app ${app}
