# -*- coding: utf-8 -*-
"""
    app.models
    ~~~~~~~~~~

    Provides the SQLAlchemy models
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import savalidation.validators as val

from datetime import datetime as dt
from savalidation import ValidationMixin

from app import db


class Age(db.Model, ValidationMixin):
    # auto keys
    utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
    utc_updated = db.Column(
        db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

    # other keys
    dataset_id = db.Column(db.String(128), primary_key=True)
    dataset_name = db.Column(db.String(128), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    needs_update = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(32), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    frequency_category = db.Column(db.String(32), nullable=False)
    dataset_title = db.Column(db.String(128), nullable=False)
    downloads = db.Column(db.Integer, nullable=False)

    # validation
    val.validates_constraints()

    def __repr__(self):
        return '<Age(%r)>' % self.dataset_name
