#!/bin/bash
# Git clone the forked common IOC repos into your local working directory.


gh repo list janeliu-slac --limit 2000 | while read -r repo _; do
  if [[ $repo == janeliu-slac/ioc-common* ]] ;
  then
    gh repo clone "$repo"
  fi
done
