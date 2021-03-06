### Copyright (C) 2005-2015 Peter Williams <pwil3058@gmail.com>
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; version 2 of the License only.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

from gi.repository import Gtk
from gi.repository import GObject

from ...bab import CmdFailure
from ...bab import enotify
from ...bab import os_utils

from ...gtx import actions
from ...gtx import dialogue
from ...gtx import doop
from ...gtx import file_tree
from ...gtx import gutils
from ...gtx import xtnl_edit

from ... import pm
from ... import scm
from . import pm_gui_ifce
from . import pm_actions
from . import pm_do_opn_files

from ...scm.gui import scm_gui_ifce
from ...scm.gui import scm_actions

from ... import wsm_icons

#          <menuitem action="peruse_files"/>
#          <menuitem action="pm_copy_files_to_top_patch"/>
#          <menuitem action="pm_move_files_in_top_patch"/>

class WSTreeModel(file_tree.FileTreeModel):
    UPDATE_EVENTS = os_utils.E_FILE_CHANGES|scm.E_NEW_SCM|scm.E_FILE_CHANGES|pm.E_FILE_CHANGES|pm.E_PATCH_STACK_CHANGES|pm.E_PATCH_REFRESH|pm.E_POP|pm.E_PUSH|scm.E_WD_CHANGES
    AU_FILE_CHANGE_EVENT = scm.E_FILE_CHANGES|os_utils.E_FILE_CHANGES # event returned by auto_update() if changes found
    @staticmethod
    def _get_file_db():
        return scm_gui_ifce.SCM.get_wd_file_db()

class WSTreeView(file_tree.FileTreeView, enotify.Listener,
                 scm_actions.WDListenerMixin, pm_actions.WDListenerMixin,
                 doop.DoOperationMixin, pm_do_opn_files.PMDoOpnFilesMixin):
    MODEL = WSTreeModel
    UI_DESCR = \
    """
    <ui>
      <menubar name="scm_files_menubar">
        <menu name="scm_files_menu" action="scm_files_menu_files">
          <menuitem action="refresh_files"/>
          <menuitem action="pm_add_new_file"/>
        </menu>
      </menubar>
      <popup name="files_popup">
          <menuitem action="delete_fs_items"/>
          <menuitem action="new_file"/>
        <separator/>
          <menuitem action="copy_fs_items"/>
          <menuitem action="move_fs_items"/>
          <menuitem action="rename_fs_item"/>
      </popup>
      <popup name="scmic_files_popup"/>
      <popup name="pmic_files_popup">
        <separator/>
          <menuitem action="pm_edit_files_in_top_patch"/>
        <separator/>
          <menuitem action="pm_add_files_to_top_patch"/>
          <menuitem action="pm_move_files_in_top_patch"/>
          <menuitem action="pm_delete_files_in_top_patch"/>
        <separator/>
        <separator/>
          <menuitem action="pm_copy_file_to_top_patch"/>
          <menuitem action="pm_rename_file_in_top_patch"/>
        <separator/>
          <menuitem action="pm_select_unsettled"/>
        <separator/>
      </popup>
    </ui>
    """
    DIRS_SELECTABLE = False
    def __init__(self, show_hidden=False, hide_clean=False):
        file_tree.FileTreeView.__init__(self, show_hidden=show_hidden, hide_clean=hide_clean)
        enotify.Listener.__init__(self)
        scm_actions.WDListenerMixin.__init__(self)
        pm_actions.WDListenerMixin.__init__(self)
        self._update_popup_cb()
        self.add_notification_cb(pm.E_PATCH_STACK_CHANGES|pm.E_NEW_PM|enotify.E_CHANGE_WD, self._update_popup_cb)
    def _update_popup_cb(self, **kwargs):
        if pm_gui_ifce.PM.is_poppable:
            self.set_popup("/pmic_files_popup")
        elif scm_gui_ifce.SCM.in_valid_wspce:
            self.set_popup("/scmic_files_popup")
        else:
            self.set_popup(self.DEFAULT_POPUP)
    def populate_action_groups(self):
        self.action_groups[actions.AC_DONT_CARE].add_actions(
            [
                ("scm_files_menu_files", None, _("_Files")),
            ])
        self.action_groups[pm_actions.AC_IN_PM_PGND + pm_actions.AC_PMIC + actions.AC_SELN_MADE].add_actions(
            [
                ("pm_add_files_to_top_patch", Gtk.STOCK_ADD, _("_Add"), None,
                 _("Add the selected files to the top patch"),
                 lambda _action=None: self.pm_do_add_files(self.get_selected_fsi_paths())
                ),
                ("pm_move_files_in_top_patch", wsm_icons.STOCK_RENAME, _("_Move"), None,
                 _("Move the selected files within the top patch"),
                 lambda _action=None: self.pm_do_move_files(self.get_selected_fsi_paths())
                ),
                ("pm_edit_files_in_top_patch", Gtk.STOCK_EDIT, _("_Edit"), None,
                 _("Open the selected files for editing after adding them to the top patch"),
                 lambda _action=None: self.pm_do_edit_files(self.get_selected_fsi_paths())
                ),
                ("pm_delete_files_in_top_patch", Gtk.STOCK_DELETE, _("_Delete"), None,
                 _("Add the selected files to the top patch and then delete them"),
                 lambda _action=None: self.pm_do_delete_files(self.get_selected_fsi_paths())
                ),
            ])
        self.action_groups[pm_actions.AC_IN_PM_PGND + pm_actions.AC_PMIC + actions.AC_SELN_UNIQUE].add_actions(
            [
                ("pm_copy_file_to_top_patch", Gtk.STOCK_COPY, _("_Copy"), None,
                 _("Add a copy of the selected file to the top patch"),
                 lambda _action=None: self.pm_do_copy_file(self.get_selected_fsi_path())
                ),
                ("pm_rename_file_in_top_patch", wsm_icons.STOCK_RENAME, _("_Rename"), None,
                 _("Rename the selected file within the top patch"),
                 lambda _action=None: self.pm_do_rename_file(self.get_selected_fsi_path())
                ),
            ])
        self.action_groups[pm_actions.AC_IN_PM_PGND + pm_actions.AC_PMIC].add_actions(
            [
                ("pm_add_new_file", Gtk.STOCK_NEW, _("New"), None,
                 _("Add a new file to the top applied patch"),
                 lambda _action=None: self.pm_do_add_new_file()
                ),
                ("pm_select_unsettled", None, _("Select _Unsettled"), None,
                 _("Select files that are unrefreshed in patches below top or have uncommitted SCM changes not covered by an applied patch"),
                 lambda _action=None: self.pm_select_unsettled()
                ),
            ])
    def pm_select_unsettled(self):
        unsettled = pm_gui_ifce.PM.get_outstanding_changes_below_top()
        filepaths = [filepath for filepath in unsettled.unrefreshed]
        filepaths += [filepath for filepath in unsettled.uncommitted]
        self.select_filepaths(filepaths)

class WSFilesWidget(file_tree.FileTreeWidget):
    MENUBAR = "/scm_files_menubar"
    BUTTON_BAR_ACTIONS = ["show_hidden_files", "hide_clean_files"]
    TREE_VIEW = WSTreeView
    @staticmethod
    def get_menu_prefix():
        return scm_gui_ifce.SCM.name
