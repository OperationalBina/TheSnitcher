
import zerorpc
import gevent
import argparse
import json
import sys
import inspect
import os
import logging
import collections
from pprint import pprint



#
# def zerorpc_inspect_legacy(client, filter_method, long_doc, include_argspec):
#     if filter_method is None:
#         remote_methods = client._zerorpc_list()
#     else:
#         remote_methods = [filter_method]
#
#     def remote_detailled_methods():
#         for name in remote_methods:
#             if include_argspec:
#                 argspec = client._zerorpc_args(name)
#             else:
#                 argspec = None
#             docstring = client._zerorpc_help(name)
#             if docstring and not long_doc:
#                 docstring = docstring.split('\n', 1)[0]
#             yield (name, argspec, docstring if docstring else '<undocumented>')
#
#     if not include_argspec:
#         longest_name_len = max(len(name) for name in remote_methods)
#         return (longest_name_len, ((name, doc) for name, argspec, doc in
#             remote_detailled_methods()))
#
#     r = [(name + (inspect.formatargspec(*argspec)
#                   if argspec else '(...)'), doc)
#          for name, argspec, doc in remote_detailled_methods()]
#     longest_name_len = max(len(name) for name, doc in r) if r else 0
#     return (longest_name_len, r)
#
# # handle the 'python formatted' _zerorpc_inspect, that return the output of
# # "getargspec" from the python lib "inspect". A monstruosity from protocol v2
#
# def zerorpc_inspect_python_argspecs(remote_methods, filter_method, long_doc, include_argspec):
#     def format_method(name, argspec, doc):
#         if include_argspec:
#             name += (inspect.formatargspec(*argspec) if argspec else
#                 '(...)')
#         if not doc:
#             doc = '<undocumented>'
#         elif not long_doc:
#             doc = doc.splitlines()[0]
#         return (name, doc)
#     r = [format_method(*methods_info) for methods_info in remote_methods if
#          filter_method is None or methods_info[0] == filter_method]
#     if not r:
#         return None
#     longest_name_len = max(len(name) for name, doc in r) if r else 0
#     return (longest_name_len, r)
#
#
# # Handles generically formatted arguments (not tied to any specific programming language).
# def zerorpc_inspect_generic(remote_methods, filter_method, long_doc, include_argspec):
#     def format_method(name, args, doc):
#         if include_argspec:
#             def format_arg(arg):
#                 def_val = arg.get('default')
#                 if def_val is None:
#                     return arg['name']
#                 return '{0}={1}'.format(arg['name'], def_val)
#
#             if args:
#                 name += '({0})'.format(', '.join(map(format_arg, args)))
#             else:
#                 name += '(??)'
#
#         if not doc:
#             doc = '<undocumented>'
#         elif not long_doc:
#             doc = doc.splitlines()[0]
#         return (name, doc)
#
#     methods = [format_method(name, details['args'], details['doc'])
#             for name, details in remote_methods.items()
#             if filter_method is None or name == filter_method]
#
#     longest_name_len = (max(len(name) for name, doc in methods)
#             if methods else 0)
#     return (longest_name_len, methods)
#
#
# def zerorpc_inspect(client, method=None, long_doc=True, include_argspec=True):
#     try:
#         inspect_result = client._zerorpc_inspect()
#         remote_methods = inspect_result['methods']
#         legacy = False
#     except (zerorpc.RemoteError, NameError):
#         legacy = True
#
#     if legacy:
#         try:
#             service_name = client._zerorpc_name()
#         except (zerorpc.RemoteError):
#             service_name = 'N/A'
#
#         (longest_name_len, detailled_methods) = zerorpc_inspect_legacy(client,
#                 method, long_doc, include_argspec)
#     else:
#         service_name = inspect_result.get('name', 'N/A')
#         if not isinstance(remote_methods, dict):
#             (longest_name_len,
#                 detailled_methods) = zerorpc_inspect_python_argspecs(
#                 remote_methods, method, long_doc, include_argspec)
#
#         (longest_name_len, detailled_methods) = zerorpc_inspect_generic(
#             remote_methods, method, long_doc, include_argspec)
#
#     return longest_name_len, detailled_methods, service_name


class Cooler(object):
    """ Various convenience methods to make things cooler. """

    def __init__(self):
        self.components = {
            "a": ["a, b, c"],
            "b": ["d, e, f"],
            "c": ["g, h, i"]
        }

    def ls(self):
        ret_str = {}
        for comp in self.components:
            ret_str[comp] = self.components.get(comp)
        return ret_str

def add_man(sentence):
    """ End a sentence with ", man!" to make it sound cooler, and
    return the result. """
    return sentence + ", man!"

def add_42(n):
    """ Add 42 to an integer argument to make it cooler, and return the
    result. """
    return n + 42

def boat(sentence):
    """ Replace a sentence with "I'm on a boat!", and return that,
    because it's cooler. """
    return "I'm on a boat!"

methods = {"1": add_man,
           "2": add_42}

methods2 = {"boat": boat}


from gevent import Greenlet

s1 = zerorpc.Server(methods)
s1.bind("tcp://0.0.0.0:4243")
g1 = Greenlet(s1.run)
g1.start()

s2 = zerorpc.Server(methods2)
s2.bind("tcp://0.0.0.0:4244")
g2 = Greenlet(s2.run)
g2.start()

c1 = zerorpc.Client()
c1.connect("tcp://127.0.0.1:4243")
# print c.hello("RPC")

c2 = zerorpc.Client()
c2.connect("tcp://127.0.0.1:4244")
# c.hello("RPC")


def s1(method=None, *args):
    return c1.__call__(method, *args)


def s2(method=None, *args):
    return c2.__call__(method, *args)


links = {"s1": s1,
         "s2": s2}

s3 = zerorpc.Server(links)
s3.bind("tcp://0.0.0.0:4242")
s3.run()
