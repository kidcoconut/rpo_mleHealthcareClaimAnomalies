#!/bin/bash -e

#--- Name:  bootstrap_gitSparse.sh
#--- Obj:   To ready the git env with sparse checkout based on workflow identity, eg mle, appDev, deploy


#--- set env vars
SCRIPTNAME=$0
WORKFLOW=$1


#--- exit the script with logMsg
die() {
   echo "$SCRIPTNAME: $1"
   exit 1
}



case $WORKFLOW in
"release")
   #--- for deploy of running app
   FOLDERS="demo"
   ;;
"mle")
   FOLDERS="notebooks"
   ;;
"docs")
   FOLDERS="docs"
   ;;
"publish")
   FOLDERS="demo docs notebooks"
   ;;
"disable")
   echo "INFO:  Running 'git sparse-checkout disable'"
   git sparse-checkout disable
   die "INFO:  done"
   ;;
*)
   die "WARN:  please specify a valid workflow"
   ;;
esac


#--- execute git sparse checkout cmds
echo "INFO:  Running 'git sparse-checkout init --cone'"
git sparse-checkout init --cone

echo "INFO:  Running 'git sparse-checkout set $FOLDERS'"
git sparse-checkout set $FOLDERS
