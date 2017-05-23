"""
Define all possible request exceptions of the API.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import boto
import logging
from flask import jsonify
from uuid import uuid4
from logger import log_exception
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions


def configure_exceptions(app, api=None):
    """Configure exception handler for Flask and Flask-Restful."""
    for code in default_exceptions:
        app.errorhandler(code)(handle_error)
    if api:
        api.handle_error = handle_error


def handle_error(e):
    """
    Handle for exceptions thrown and returns a Flask JSON reponse.

    Parameters
    ----------
    e : Exception
        An exception that is raised in the application.
    """
    code = 500
    message = str(e)
    error_id = uuid4()

    # ValueError (parameter validation)
    if isinstance(e, ValueError):
        code = 400
        message = str(e)

    # Generic
    if isinstance(e, HTTPException):
        code = e.code
        message = e.description
        if hasattr(e, 'data') and 'message' in e.data:
            message = str(e.data['message'])
        log_exception(logging.getLogger('application'), error_id, message)

    # DynamoDB
    if isinstance(e, boto.exception.JSONResponseError):
        code, message = handle_dynamo_error(e)
        log_exception(logging.getLogger('boto'), error_id, message)

    return jsonify(message=message, code=code, error_id=error_id), code


def handle_dynamo_error(e):
    """
    Handle a dynamo exception and return (code, message) tuple.

    Parameters
    ----------
    e : flask_dynamo.errors
        Error raised by flask dynamo

    Returns
    -------
    tuple
        (code, message)
    """
    if isinstance(e, boto.exception.JSONResponseError):
        return(400, str(e.message))
    return (500, str(e))


class BadRequest(HTTPException):
    """
    400 Bad Request.

    The request sent was malformed and could not be understood.
    """

    code = 400
    description = (
        'Bad request, the request could not be understood by the server '
        'due to malformed syntax'
    )


class Unauthorized(HTTPException):
    """
    401 Unauthorized.

    Not authorized on the server.
    """

    code = 401
    description = (
        'Unauthorized, bad credentials'
    )


class Forbidden(HTTPException):
    """
    403 Forbidden.

    Not allowed to access this resource.
    """

    code = 403
    description = (
        'Forbidden, neccesary permissions are not granted for the resource'
    )


class NotFound(HTTPException):
    """
    404 Not Found.

    This resource does not exist here.
    """

    code = 404
    message = (
        'Not found, the requested resource is not here'
    )


class MethodNotAllowed(HTTPException):
    """
    405 Method Not Allowed.

    The method used is not allowed for this call.
    """

    code = 405
    description = (
        'Method not allowed, The HTTP method is not allowed for this resource'
    )


class InvalidAPIVersion(HTTPException):
    """
    406 Invalid API Version.

    The version specified is not acceptable.
    """

    code = 406
    description = (
        'API version is missing or invalid'
    )


class RateLimitExceeded(HTTPException):
    """
    429 Rate Limit Exceeded.

    Too many requests were sent too fast.
    """

    code = 429
    description = (
        'Rate limit exceeded, too many requests too quickly'
    )


class ServerError(HTTPException):
    """
    500 Server Error.

    Something went completely wrong.
    """

    code = 500
    description = (
        'Server error, The server encountered an unexpected condition '
        'which prevented it from fulfilling the request'
    )


class ServiceUnavailable(HTTPException):
    """
    503 Service Unavailable.

    Server overload or under maintainance.
    """

    code = 503
    description = (
        'Server unable to handle request due to temporary overloading or '
        'maintainance of the server'
    )