#!/bin/bash

env GO111MODULE=off \
    go run tls-proxy.go \
    -front 0.0.0.0:$2 \
    -back 0.0.0.0:$1 \
    -cert ./public.pem \
    -key ./private.pem