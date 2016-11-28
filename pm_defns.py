#  Copyright 2016 Peter Williams <pwil3058@gmail.com>
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License only.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; if not, write to:
#  The Free Software Foundation, Inc., 51 Franklin Street,
#  Fifth Floor, Boston, MA 02110-1301 USA

"""Enumerations, constants etcetera for use by Patch Managers"""

__all__ = ["PatchData", "PatchState", "Presence", "Validity", "FileStatus", "PatchTableRow"]
__author__ = "Peter Williams <pwil3058@gmail.com>"

import collections

PatchData = collections.namedtuple("PatchData", ["name", "state", "guards"])

class PatchState:
    NOT_APPLIED = " "
    APPLIED_REFRESHED = "+"
    APPLIED_NEEDS_REFRESH = "?"
    APPLIED_UNREFRESHABLE = "!"

class Presence(object):
    from ..patch_diff import patches
    ADDED = patches.FilePathPlus.ADDED
    REMOVED = patches.FilePathPlus.DELETED
    EXTANT = patches.FilePathPlus.EXTANT

class Validity(object):
    REFRESHED, NEEDS_REFRESH, UNREFRESHABLE = range(3)

class FileStatus(collections.namedtuple("FileStatus", ["presence", "validity"])):
    def __str__(self):
        return self.presence

PatchTableRow = collections.namedtuple("PatchTableRow", ["name", "state", "pos_guards", "neg_guards"])
