"""flatty - marshaller/unmarshaller for light-schema python objects"""
VERSION = (0, 1, 2)
__version__ = ".".join(map(str, VERSION))
__author__ = "Christian Haintz"
__contact__ = "christian.haintz@orangelabs.at"
__homepage__ = "http://packages.python.org/flatty"
__docformat__ = "restructuredtext"


from flatty import *
try:
    import couch
except ImportError:
    pass
try:
    import mongo
except ImportError:
    pass