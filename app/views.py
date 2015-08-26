# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~

    Provides additional API endpoints
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from flask import Blueprint, request
from rq import Queue
from loremipsum import get_sentences
from ckanutils import CKAN

from config import Config as c
from app import cache, __version__, utils
from app.utils import jsonify, make_cache_key, parse
from app.connection import conn

q = Queue(connection=conn)
blueprint = Blueprint('blueprint', __name__)
cache_timeout = 60 * 60 * 1  # hours (in seconds)


@blueprint.route('%s/status/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout, key_prefix=make_cache_key)
def status():
    kwargs = {k: parse(v) for k, v in request.args.to_dict().items()}
    ckan = CKAN(**kwargs)

    resp = {
        'online': True,
        'message': 'Service for checking and updating HDX dataset ages.',
        'CKAN_instance': ckan.address,
        'version': __version__,
        'repository': 'https://github.com/reubano/HDX-Age-API'
    }

    return jsonify(**resp)


@blueprint.route('%s/lorem/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout, key_prefix=make_cache_key)
def lorem():
    resp = {'result': get_sentences(1)[0]}
    return jsonify(**resp)


@blueprint.route('%s/test/' % c.API_URL_PREFIX)
@blueprint.route('%s/test/<word>/' % c.API_URL_PREFIX)
def test(word=''):
    kwargs = {k: parse(v) for k, v in request.args.to_dict().items()}
    sync = kwargs.pop('sync', False)

    if sync:
        resp = {'result': utils.count_letters(word)}
    else:
        job = q.enqueue(utils.count_letters, word)
        result_url = 'http://%s:%s%s/result/%s' % (
            c.HOST, c.PORT, c.API_URL_PREFIX, job.id)

        resp = {
            'job_id': job.id,
            'job_status': job.get_status(),
            'result_url': result_url}

    return jsonify(**resp)


@blueprint.route('%s/update/' % c.API_URL_PREFIX)
@blueprint.route('%s/update/<pid>/' % c.API_URL_PREFIX)
def update(pid=None):
    kwargs = {k: parse(v) for k, v in request.args.to_dict().items()}
    sync = kwargs.pop('sync', False)

    try:
        chunk_size = int(kwargs.pop('chunk_size'))
    except KeyError:
        chunk_size = None

    if sync:
        resp = {'result': utils.update(pid, chunk_size, **kwargs)}
    else:
        job = q.enqueue(utils.update, pid, chunk_size, **kwargs)
        result_url = 'http://%s:%s%s/result/%s/' % (
            c.HOST, c.PORT, c.API_URL_PREFIX, job.id)

        resp = {
            'job_id': job.id,
            'job_status': job.get_status(),
            'result_url': result_url}

    return jsonify(**resp)


@blueprint.route('%s/result/<jid>/' % c.API_URL_PREFIX)
def result(jid):
    job = q.fetch_job(jid)
    job_status = job.get_status()
    statuses = {'queued': 202, 'started': 202, 'finished': 200, 'failed': 500}

    resp = {
        'status': statuses[job_status],
        'job_id': job.id,
        'job_status': job_status,
        'result': job.result}

    return jsonify(**resp)


@blueprint.route('%s/double/<num>/' % c.API_URL_PREFIX)
@cache.memoize(timeout=cache_timeout)
def double(num):
    resp = {'result': 2 * num}
    return jsonify(**resp)


@blueprint.route('%s/delete/<base>/' % c.API_URL_PREFIX)
def delete(base):
    url = request.url.replace('delete/', '')
    cache.delete(url)
    return jsonify(result='Key: %s deleted' % url)


@blueprint.route('%s/reset/' % c.API_URL_PREFIX)
def reset():
    cache.clear()
    return jsonify(result='Caches reset')