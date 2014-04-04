# -*- coding: utf-8 -*-
#
# This file is part of Calypso Server - Calendar Server
# Copyright © 2013 Joseph Nahmias
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
PAM authentication

Use Pluggable Authentication Modules (PAM) system on Linux
for checking users/passwords.

"""

import logging
import PAM

from calypso import config

LOG = logging.getLogger()
SVC = config.get("acl", "pam_service")

def has_right(entity, user, password):
    """Check if ``user``/``password`` couple is valid."""
    LOG.debug("entity %s user %s", entity, user)
    if entity.owner and entity.owner != user and entity.personal:
        return False
    def pam_conv(auth, query_list, userData):
        result = []
        result.append((password, 0))
        return result
    try:
        auth = PAM.pam()
        auth.start(SVC)
        auth.set_item(PAM.PAM_USER, user)
        auth.set_item(PAM.PAM_CONV, pam_conv)
        auth.authenticate()
        auth.acct_mgmt()
        return True
    except PAM.error, resp:
        LOG.debug('PAM error: %s', resp)
    return False

# vi: set ts=4 sw=4 et si :
