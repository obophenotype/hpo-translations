#!/bin/sh
# Wrapper script for docker.
#
# This is used primarily for wrapping the GNU Make workflow.
# Instead of typing "make TARGET", type "./run.sh make TARGET".
# This will run the make workflow within a docker container.
#
# The assumption is that you are working in the src/ontology folder;
# we therefore map the whole repo (../..) to a docker volume.
#
# See README-editors.md for more details.

IMAGE=${IMAGE:-odkfull}
ODK_JAVA_OPTS=-Xmx20G
ODK_DEBUG=${ODK_DEBUG:-yes}

TIMECMD=
if [ x$ODK_DEBUG = xyes ]; then
    echo "Running ${IMAGE} with ${ODK_JAVA_OPTS} of memory for ROBOT and Java-based pipeline steps."
    TIMECMD="/usr/bin/time"
fi

docker run -v "$PWD/:/work" -w /work -e ROBOT_JAVA_ARGS="$ODK_JAVA_OPTS" -e JAVA_OPTS="$ODK_JAVA_OPTS" --rm -ti obolibrary/$IMAGE $TIMECMD "$@"

case "$@" in
*update_repo*|*release*)
    echo "Please remember to update your ODK image from time to time: https://oboacademy.github.io/obook/howto/odk-update/."
    ;;
esac
