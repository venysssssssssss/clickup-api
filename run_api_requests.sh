#!/bin/bash

urls=("$@")

for url in "${urls[@]}"; do
  echo "Fetching: $url"
  response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$?" -ne 0 ]; then
    echo "Failed to fetch $url"
    exit 1
  fi
  echo "Response code: $response"
done
