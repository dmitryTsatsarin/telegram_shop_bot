# -*- coding: utf-8 -*-
__author__ = 'forward'
import socket

if socket.gethostname() == 'forward-G75VX':
    from .local import *
else:
    from .prod import *
