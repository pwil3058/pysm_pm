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

"""Utility functions for Patch Managers"""

__all__ = ["patch_timestamp_str", "MERGE_CRE", "generic_delete_files",
           "get_patch_file_description", "set_patch_file_description",
           "convert_patchname_to_filename"]
__author__ = "Peter Williams <pwil3058@gmail.com>"

import re
import time

from ..bab import options

def patch_timestamp_tz_str(tz_seconds=None):
    """Return the timezone as a string suitable for use in patch header"""
    if tz_seconds is None:
        tz_seconds = -time.timezone
    if tz_seconds > 0:
        hrs = tz_seconds / 3600
    else:
        hrs = -(-tz_seconds / 3600)
    mins = (abs(tz_seconds) % 3600) / 60
    return "{0:0=+3}{1:02}".format(hrs, mins)

_PTS_TEMPL = "%Y-%m-%d %H:%M:%S.{0:09} " + patch_timestamp_tz_str()

def patch_timestamp_str(secs=None):
    """Return the "in patch" timestamp string for "secs" seconds"""
    ts_str = time.strftime(_PTS_TEMPL, time.localtime(secs))
    return ts_str.format(int((secs % 1) * 1000000000))

MERGE_CRE = re.compile("^(<<<<<<<|>>>>>>>).*$")

def generic_delete_files(file_paths):
    from ..bab import os_utils
    return os_utils.os_delete_files(file_paths, events=pm.EFILE_DELETED)

def set_patch_file_description(patch_file_path, description, overwrite=False):
    from ..patch_diff import patches
    from ..bab import utils
    if os.path.isfile(patch_file_path):
        try:
            patch_obj = patches.Patch.parse_text(utils.get_file_contents(patch_file_path))
        except IOError as edata:
            return CmdResult.error(stderr=str(edata))
        except patches.ParseError:
            if overwrite:
                patch_obj = patches.Patch()
            else:
                return CmdResult.error(stderr=_("{0}: exists but is not a valid patch file".format(patch_file_path))) | CmdResult.Suggest.OVERWRITE
    else:
        patch_obj = patches.Patch()
    patch_obj.set_description(description)
    result = utils.set_file_contents(patch_file_path, str(patch_obj), compress=True)
    return result

def get_patch_file_description(patch_file_path):
    assert os.path.isfile(patch_file_path), _("Patch file \"{0}\" does not exist\n").format(patch_file_path)
    from ..patch_diff import patches
    from ..bab import utils
    pobj = patches.Patch.parse_text(utils.get_file_contents(patch_file_path))
    return pobj.get_description()

options.define("export", "replace_spc_in_name_with", options.Defn(str, None, _("Character to replace spaces in patch names with during export")))

def convert_patchname_to_filename(patchname):
    import re
    repl = options.get("export", "replace_spc_in_name_with")
    if isinstance(repl, str):
        return re.sub("(\s+)", repl, patchname.strip())
    else:
        return patchname
