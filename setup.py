#!/usr/bin/env python3
from setuptools import setup, find_packages

required = [
    "mongoengine",
    "Flask",
    "flask_mongoengine",
    "flask-smorest",
    "marshmallow",
    "pytz",
    "gunicorn",
    "environs",
    "passlib",
    "redis",
    "solders",       # Solana SDK for Python
    "anchorpy",      # Python wrapper for Anchor programs on Solana
    "base58",
    "pynacl"
]

VERSION = "2025.1.0"

setup(
      name='dao-api',
      version=VERSION,
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=required,
)
