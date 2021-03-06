"""Application factory for external relations service."""

from flask import Flask, Response, jsonify
from werkzeug.exceptions import HTTPException, Forbidden, Unauthorized, \
    BadRequest, MethodNotAllowed, InternalServerError, NotFound

from arxiv.base import Base, logging
from arxiv.base.middleware import wrap, request_logs
from arxiv.users import auth

from . import routes


def create_ui_app() -> Flask:
    """Create a new UI application."""
    app = Flask('funding')
    app.config.from_pyfile('config.py')
    Base(app)
    auth.Auth(app)
    app.register_blueprint(routes.ui.blueprint)
    wrap(app, [auth.middleware.AuthMiddleware])
    register_error_handlers(app)
    return app


def create_api_app() -> Flask:
    """Create a new API application."""
    app = Flask('funding')
    app.config.from_pyfile('config.py')
    Base(app)
    auth.Auth(app)
    app.register_blueprint(routes.api.blueprint)
    wrap(app, [auth.middleware.AuthMiddleware])
    register_error_handlers(app)
    return app


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the Flask app."""
    app.errorhandler(Forbidden)(jsonify_exception)
    app.errorhandler(Unauthorized)(jsonify_exception)
    app.errorhandler(BadRequest)(jsonify_exception)
    app.errorhandler(InternalServerError)(jsonify_exception)
    app.errorhandler(NotFound)(jsonify_exception)
    app.errorhandler(MethodNotAllowed)(jsonify_exception)


def jsonify_exception(error: HTTPException) -> Response:
    """Render exceptions as JSON."""
    exc_resp = error.get_response()
    response: Response = jsonify(reason=error.description)
    response.status_code = exc_resp.status_code
    return response
