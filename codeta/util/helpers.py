"""
    Contains various helper classes to write cleaner code
"""

class Callable():
    """ A wrapper to let you create static class functions """
    def __init__(self, anycallable):
        self.__call__ = anycallable
