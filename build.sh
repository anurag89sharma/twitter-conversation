#!/bin/bash -e

BASEDIR=`dirname $0`

if [ ! -d "$BASEDIR/venv" ]; then
    virtualenv -q $BASEDIR/venv --no-site-packages
    echo "Virtualenv created."
fi

if [ ! -f "$BASEDIR/venv/updated" -o $BASEDIR/requirements.txt -nt $BASEDIR/ve/updated ]; then
	source $BASEDIR/venv/bin/activate
    pip install -r $BASEDIR/requirements.txt
    echo "Requirements installed."
fi

echo "Deploying the app."
echo "App Deployed. Open this link - http://127.0.0.1:8010/ in a web browser"
$(python $BASEDIR/twitter-conversation/manage.py runserver 8010)
echo "App Deployed. Open this link - http://127.0.0.1:8010/ in a web browser"