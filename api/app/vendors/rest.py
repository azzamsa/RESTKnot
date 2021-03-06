import json
from datetime import date, datetime

from flask import Response


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError("Type %s not serializable" % type(obj))


def response(status_code, message=None, data=None):
    """Response data helper

    Arguments:
        status_code {int} -- http status code

    Keyword Arguments:
        message {string} -- response message (default: {None})
        data {dict} -- data to be appended to response (default: {None})

    Returns:
        dict -- response data
    """
    success_status = {
        200: "OK",
        201: "Created",
        202: "Accepted",
        204: "No Content",
        304: "Not modified",
    }

    failure_status = {
        400: "Internal error occurred - unexpected error caused by request data",
        401: "Unauthorized operation",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed, for example, resource doesn't support DELETE method",
        406: "Method Not Acceptable",
        409: "Conflict",
        422: "Unprocessable Entity",
        423: "Locked",
        426: "Upgrade Required",
        500: "Internal Server Error",
        501: "Not Implemented - functionality is not implemented on the server side",
        503: "Service is unavailable",
    }

    status = {}
    status["code"] = status_code

    if status_code in success_status:
        count = 0
        if type(data) is list:
            count = len(data)
        if type(data) is dict:
            count = 1
        status["count"] = count
        status["data"] = data if data else None
        status["status"] = "success"
        status["message"] = message if message else success_status[status_code]
    elif status_code in failure_status:
        status["status"] = "error"
        status["message"] = message if message else failure_status[status_code]
    else:
        status["status"] = "error"
        status["message"] = message if message else failure_status[400]

    response = Response(
        response=json.dumps(status, default=json_serial),
        status=status_code,
        mimetype="application/json",
    )

    return response
