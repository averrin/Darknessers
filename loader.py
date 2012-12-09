# -*- coding: utf-8 -*-
"""
    Загрузчик модулей

    .. codeauthor:: Nabrodov Alexey <a.nabrodov@roscryptpro.ru>
"""
import os
import imp


class Loader(object):
    def __init__(self, match_cls=None, path=''):
        self.match_cls = match_cls
        self.path = path
        self.modules = []
        _modules = [self.load_module(name) for name in self.find_modules()]

        if self.match_cls:
            for module in _modules:
                if module is not None:
                    for obj in module.__dict__.values():
                        if isinstance(obj, self.match_cls):
                            self.modules.append(obj)

    def find_modules(self):
        """Return names of modules in a directory.

        Returns module names in a list. Filenames that end in ".py" or
        ".pyc" are considered to be modules. The extension is not included
        in the returned list.
        """
        modules = set()
        for filename in os.listdir(self.path):
            module = None
            if filename.endswith(".py"):
                module = filename[:-3]
            elif filename.endswith(".pyc"):
                module = filename[:-4]
            if module is not None:
                modules.add(module)
        return list(modules)

    def load_module(self, name):
        """Return a named module found in a given path."""
        (file, pathname, description) = imp.find_module(name, [self.path])
        # try:
        return imp.load_module(name, file, pathname, description)
        # except:
        #     pass
