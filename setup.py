#!/usr/bin/env python3
from setuptools import setup, find_packages

required = [
    "SQLAlchemy",
    "Flask",
    "Flask-SQLAlchemy",
    "flask-smorest",
    "marshmallow",
    "pytz",
    "gunicorn",
    "environs",
    "passlib",
    "redis",
]

VERSION = "2025.1.0"

setup(
      name='dao-api',
      version=VERSION,
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=required,
)
