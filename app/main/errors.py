# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, current_app
from . import bp


@bp.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    current_app.logger.error('Unauthorized: %s', (request.path))
    return render_template('errors/403.html'), 403


@bp.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    if not request.path.endswith("robots.txt"):
        current_app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(400)
def forbidden(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'bad request'})
        response.status_code = 400
        return response
    current_app.logger.error('Bad request: %s', (request.path))
    return render_template('errors/500.html'), 400


@bp.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    current_app.logger.error('Server Error: {}, {}'.format(request.path, e))
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(Exception)
def unhandled_exception(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'unhandled exception'})
        response.status_code = 500
        return response
    current_app.logger.error('Unhandled exception: {}, {}'.format(request.path, e))
    return render_template('errors/500.html'), 500
