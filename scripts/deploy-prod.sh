#! /usr/bin/env sh

# Exit in case of error
set -e

docker push 10.0.0.95:5000/pcr/user_management:v0.1.0-beta
docker push 10.0.0.95:5000/pcr/queue_user_management:v0.1.0-beta