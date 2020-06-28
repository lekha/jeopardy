#!/usr/bin/env python
import sys
from unittest.mock import patch

from pymysql.constants import CLIENT
from yoyo.connections import parse_uri
from yoyo.scripts.main import main


def _parse_uri(uri):
    """Patch original yoyo's parse_uri() function.

    This patch adds the client_flag CLIENT_MULTI_STATEMENTS for mysql backends
    powered by the pymysql driver. This is used to execute multiple queries in
    a single migration step instead of going through the hassle of breaking up
    some steps that don't make sense to break up in the first place.
    """
    result = parse_uri(uri)
    if result.scheme == "mysql":
        result.args["client_flag"] = CLIENT.MULTI_STATEMENTS
    return result


@patch("yoyo.connections.parse_uri", _parse_uri)
def patched_yoyo(argv):
    main(argv)


if __name__ == "__main__":
    patched_yoyo(sys.argv[1:])
