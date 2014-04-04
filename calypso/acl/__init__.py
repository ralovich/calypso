# -*- coding: utf-8 -*-
#
# This file is part of Calypso Server - Calendar Server
# Copyright © 2008-2011 Guillaume Ayoub
# Copyright © 2008 Nicolas Kandel
# Copyright © 2008 Pascal Halter
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Calypso.  If not, see <http://www.gnu.org/licenses/>.

"""
Users and rights management.

This module loads a list of users with access rights, according to the acl
configuration.

"""

from calypso import config


def load():
    """Load list of available ACL managers."""
    acl_type = config.get("acl", "type").encode("utf-8")
    module = __import__("calypso.acl", fromlist=[acl_type])
    return getattr(module, acl_type)

class Entity(object):
    """Interface for resources, uses to check them against an ACL."""

    owner = None

    def is_personal(self):
        return True

    def has_right(self, user):
        """Return true if a given user may access the resource"""

        # this implementation is always personal; non-collection resources are
        # not expected to be accessed by different users.

        return (user == self.owner if self.owner else True) if self.is_personal() else True
