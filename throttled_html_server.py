#!/usr/bin/env python -3

"""
    throttled html server
    =====================

    For web page loading tests.

    :copyleft: 2014 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import BaseHTTPServer
import io
import os
import time
import webbrowser


HOST_NAME = "127.0.0.1"
PORT_NUMBER = 8000


class ThrottleHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    CHUNK_SIZE = 400 * 1024
    CHUNK_SLEEP = 0.2

    STATIC_FILES_INFO = {
        ".html": ("r", "UTF-8", "text/html; charset=UTF-8"),
        ".ico": ("rb", None, "image/x-icon"),
        ".css": ("r", "UTF-8", "text/css"),
        ".js": ("r", "UTF-8", "text/javascript"),
        ".json": ("r", "UTF-8", "application/json"),
        ".mem": ("rb", None, "application/x-emscripten-blob"),
    }
    DEFAULT_STATIC_FILE_INFO = ("rb", None, "application/octet-stream")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    def do_GET(self):
        if self.path.endswith("/"):
            self.path += "index.html"

        fname, ext = os.path.splitext(self.path)

        try:
            open_mode, encoding, content_type = self.STATIC_FILES_INFO[ext]
        except KeyError:
            open_mode, encoding, content_type = self.DEFAULT_STATIC_FILE_INFO

        path = os.curdir + self.path
        local_filepath = os.path.normpath(os.path.join(self.BASE_DIR, path))

        try:
            self.log_message(
                "Send file %r mode=%r encoding=%r content_type=%r",
                local_filepath, open_mode, encoding, content_type
            )
            with io.open(local_filepath, open_mode, encoding=encoding) as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                sleep_count = 0
                while True:
                    data = f.read(self.CHUNK_SIZE)
                    if not data:
                        break
                    self.wfile.write(data)
                    sleep_count += 1
                    time.sleep(self.CHUNK_SLEEP)
                self.log_message(
                    "Send file in %i chunks and sleep total %i sec",
                    sleep_count, self.CHUNK_SLEEP * sleep_count
                )
        except IOError as err:
            raise
            self.send_error(404, message=err)


if __name__ == '__main__':
    print("Server base dir: %r" % ThrottleHandler.BASE_DIR)
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), ThrottleHandler)

    url = "http://%s:%s" % (HOST_NAME, PORT_NUMBER)
    print("Start http server on: %r" % url)
    webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

    print(" *** http server stops. *** ")