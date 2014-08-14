import xml.etree.ElementTree as ET
from . import config, paths, acl
from .xmlutils_generic import _tag

class Resource(acl.Entity):
    """Resources initially were pseudo-collections/items (so they could be
    included in the propfind loop), but currently are objects that represent
    resources on the server that are not collectons / collection items.

    Their interfaces for propfind could possibly be inherited to Collection and
    collection Item in the future."""

    def propfind(self, tag, element):
        """If self can respond to a propfind request on a tag, update the
        prepared response element with child nodes."""

    def propfind_children(self, depth, context):
        """Return a list of resources / collections / items that are to be
        responded with to a propfind of a given depth"""
        return [self]

    def do_get_head(self, request, context, is_get):
        """Handle an incoming GET or HEAD request. See
        CollectionHTTPHandler.do_get_head for what this usually should do."""
        request.send_calypso_response(404, 0)
        request.end_headers()

    urlpath = None # this should be present ... implement as abstract property?

class WellKnownDav(Resource):
    def has_right(self, user):
        return True

    def do_get_head(self, request, context, is_get):
        """According to RFC6764, redirect to a context path (from where
        current-user-principal can be discovered)"""
        request.send_calypso_response(303, 0)
        request.send_header("Location", "/")
        request.end_headers()

class Principal(Resource):
    def __init__(self, username):
        self.username = username
        self.urlpath = config.get("server", "user_principal") % {"user": self.username} # it's currently hardcoded anyway

    owner = property(lambda self: self.username)

    def propfind(self, tag, element):
        super(Principal, self).propfind(tag, element)

        # maybe move those out to generic resources; kaddressbook doesn't query
        # for current-user-princial and ask there, but plain go to the
        # requested url and propfind for home-sets
        if tag == _tag("C", "calendar-home-set"):
            tag = ET.Element(_tag("D", "href"))
            tag.text = self.urlpath + CalendarHomeSet.type_dependent_suffix + '/'
            element.append(tag)
        elif tag == _tag("A", "addressbook-home-set"):
            tag = ET.Element(_tag("D", "href"))
            tag.text = self.urlpath + AddressbookHomeSet.type_dependent_suffix + '/'
            element.append(tag)

class HomeSet(Resource):
    def __init__(self, username):
        self.username = username
        self.urlpath = config.get("server", "user_principal") % {"user": self.username} + self.type_dependent_suffix + "/" # it's currently hardcoded anyway

    owner = property(lambda self: self.username)

    def propfind_children(self, depth, context):
        # FIXME ignoring depth

        items = [c for c in paths.enumerate_collections() if self.is_in_set(c) and context['has_right'](c)]
        return super(HomeSet, self).propfind_children(depth, context) + items

class AddressbookHomeSet(HomeSet):
    type_dependent_suffix = "addressbooks"

    def is_in_set(self, collection):
        return collection.is_vcard

class CalendarHomeSet(HomeSet):
    type_dependent_suffix = "calendars"

    def is_in_set(self, collection):
        return collection.is_vcal
