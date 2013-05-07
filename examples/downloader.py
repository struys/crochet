#!/usr/bin/python
"""
A flask web application that downloads a page in the background.
"""

import logging
from flask import Flask, session, escape
from crochet import setup, run_in_reactor, retrieve_result, TimeoutError

# Can be called multiple times with no ill-effect:
setup()

app = Flask(__name__)


@run_in_reactor
def download_page(url):
    """
    Download a page.
    """
    from twisted.web.client import getPage
    return getPage(url)


@app.route('/')
def index():
    if 'download' not in session:
        # Calling an @in_reactor function returns a DefererdResult:
        result = download_page('http://www.google.com')
        session['download'] = result.stash()
        return "Starting download, refresh to track progress."

    # retrieval is a one-time operation, so session value cannot be reused:
    result = retrieve_result(session.pop('download'))
    try:
        download = result.wait(timeout=0.1)
        return "Downloaded: " + escape(download)
    except TimeoutError:
        session['download'] = result.stash()
        return "Download in progress..."


if __name__ == '__main__':
    import os, sys
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app.secret_key = os.urandom(24)
    app.run()
