#!/bin/bash

# Git clone the forked common IOC repos into /iocs

# update this with your Github username
github_username=janeliu-slac


gh repo list $github_username --limit 2000 | while read -r repo _; do
  if [[ $repo == $github_username/ioc-common* ]] ;
  then
    cd ../..
    gh repo clone "$repo"
  fi
done
