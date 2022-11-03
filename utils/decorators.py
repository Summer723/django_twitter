from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def required_params(request_attr='query_params', params=None):

    if params == None:
        params = []

    def decorator(view_func):
        pass

