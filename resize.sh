#!/usr/bin/env bash

if ! command -v convert file &> /dev/null; then
  echo "install: file, imagemagick">&2
  exit 1
elif ! [ -d ./character_info ]; then
  echo "character_info is not found."
  exit 1
fi

for i in ./character_info/*/icons/*.png; do
  file "$i" | grep -q '256 x 256' && continue
  echo "---"
  mv "$i" "${i/%/_large}"
  convert -resize 256x256 "${i/%/_large}" "$i"
  file "${i%/*}"/*
done
echo "--->done!"
