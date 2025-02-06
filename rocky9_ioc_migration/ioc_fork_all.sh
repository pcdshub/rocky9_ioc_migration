#!/bin/bash

# Git fork all common IOC repos. This script may have to be run several times due
# to limitations in github for how quickly a user can git fork a large
# number of repos. There are approximately 150 common IOC repos.

# Git fork repos that start with "ioc-common"
gh repo list pcdshub --limit 2000 | while read -r repo _; do
  if [[ $repo == pcdshub/ioc-common* ]] ;
  then
    gh repo fork "$repo" --default-branch-only --remote
  fi
done
