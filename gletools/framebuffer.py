# -*- coding: utf-8 -*-

"""
    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from __future__ import with_statement

from ctypes import byref
from pyglet.gl import *

from contextlib import nested

from .util import Context, get

__all__ = ['Framebuffer']

class Textures(object):
    def __init__(self, framebuffer):
        self.framebuffer = framebuffer
        self.textures = [None] * get(GL_MAX_COLOR_ATTACHMENTS)

    def __getitem__(self, i):
        self.textures[i]

    def __setitem__(self, i, texture):
        with nested(self.framebuffer, texture):
            glFramebufferTexture2DEXT(
                GL_FRAMEBUFFER_EXT,
                GL_COLOR_ATTACHMENT0_EXT + i,
                texture.target,
                texture.id,
                0,
            )
            self.textures[i] = texture

    def __iter__(self):
        return iter(self.textures)

class Framebuffer(Context):
    errors = {
        GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT_EXT:'GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT_EXT',
        GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT_EXT:'GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT_EXT: no image is attached',
        GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT:'GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT: attached images dont have the same size',
        GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT:'GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT: the attached images dont have the same format',
        GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER_EXT:'GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER_EXT',
        GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER_EXT:'GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER_EXT',
        GL_FRAMEBUFFER_UNSUPPORTED_EXT:'GL_FRAMEBUFFER_UNSUPPORTED_EXT',
    }
    class Exception(Exception): pass

    _get = GL_FRAMEBUFFER_BINDING
    
    def bind(self, id):
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, id)

    def check(self):
        status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
        if status != GL_FRAMEBUFFER_COMPLETE_EXT:
            desc = self.errors.get(status)
            if desc:
                raise self.Exception(desc)
            else:
                raise self.Exception('unkown framebuffer object problem')

    def __init__(self, id=None):
        Context.__init__(self) 
        self._texture = None
        self._depth = None
        id = self.id = GLuint()
        glGenFramebuffersEXT(1, byref(id))
        self.textures = Textures(self)
        
    def get_depth(self):
        return self._depth
    def set_depth(self, depth):
        self._depth = depth
        with self:
            glFramebufferRenderbufferEXT(
                GL_FRAMEBUFFER_EXT,
                GL_DEPTH_ATTACHMENT_EXT,
                GL_RENDERBUFFER_EXT,
                depth.id,
            )
    depth = property(get_depth, set_depth)
