# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

from gi.repository import GObject, Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

computer_icon = {
    "label": _('Show "Computer" icon on desktop'),
    "visible_key": "org.gnome.nautilus.desktop.computer-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.computer-icon-name",
    "icon_name": "gnome-fs-client"
}

home_icon = {
    "label": _('Show "Home Folder" icon on desktop'),
    "visible_key": "org.gnome.nautilus.desktop.home-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.home-icon-name",
    "icon_name": "gnome-fs-home"
}

trash_icon = {
    "label": _('Show "Trash" icon on desktop'),
    "visible_key": "org.gnome.nautilus.desktop.trash-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.trash-icon-name",
    "icon_name": "gnome-fs-trash-empty"
}

network_icon = {
    "label": _('Show "Network Servers" icon on desktop'),
    "visible_key": "org.gnome.nautilus.desktop.network-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.network-icon-name",
    "icon_name": "network-workgroup"
}

desktop_icons = (computer_icon, home_icon, trash_icon, network_icon)

class DesktopIcon(Gtk.VBox):
    def __init__(self, item):
        GObject.GObject.__init__(self)

        self.show_button = WidgetFactory.create("CheckButton",
                                                label=item["label"],
                                                key=item["visible_key"],
                                                backend="gsettings")
        self.show_button.connect('toggled', self.on_show_button_changed)
        self.pack_start(self.show_button, False, False, 0)

        self.show_hbox = Gtk.HBox(spacing=12)
        self.pack_start(self.show_hbox, False, False, 0)

        if not self.show_button.get_active():
            self.show_hbox.set_sensitive(False)

        icon = Gtk.Image.new_from_icon_name(item["icon_name"], Gtk.IconSize.DIALOG)
        self.show_hbox.pack_start(icon, False, False, 0)

        self.rename_button = WidgetFactory.create("StringCheckButton",
                                                  label=_('Rename'),
                                                  key=item["name_key"],
                                                  backend="gsettings")
        self.rename_button.connect('toggled', self.on_show_button_changed)
        vbox = Gtk.VBox(spacing=6)
        self.show_hbox.pack_start(vbox, False, False, 0)
        vbox.pack_start(self.rename_button, False, False, 0)

        self.entry = WidgetFactory.create("Entry", key=item["name_key"], backend="gsettings")
        self.entry.connect('insert-at-cursor', self.on_entry_focus_out)
        if not self.rename_button.get_active():
            self.entry.set_sensitive(False)
        vbox.pack_start(self.entry, False, False, 0)

    def on_entry_focus_out(self, widget, event):
        self.entry.setting.set_value(self.entry.get_text())

    def on_show_button_changed(self, widget):
        self.show_hbox.set_sensitive(self.show_button.get_active())
        active = self.rename_button.get_active()

        if active:
            self.entry.set_sensitive(True)
            self.entry.grab_focus()
        else:
            self.entry.set_sensitive(False)
            self.entry.setting.unset()
            self.entry.set_text('')


class Icon(TweakModule):
    __title__ = _('Desktop Icon Settings')
    __desc__ = _("Rename and toggle visibilty of desktop icons")
    __icon__ = 'preferences-desktop-wallpaper'
    __category__ = 'desktop'

    def __init__(self):
        TweakModule.__init__(self)

        self.show_button = WidgetFactory.create("CheckButton",
                                                label=_("Show desktop icons"),
                                                key="org.gnome.desktop.background.show-desktop-icons",
                                                backend="gsettings")
        self.show_button.connect('toggled', self.on_show_button_changed)
        self.add_start(self.show_button, False, False, 0)

        self.show_button_box = Gtk.HBox(spacing=12)
        self.add_start(self.show_button_box, False, False, 0)

        if not self.show_button.get_active():
            self.show_button_box.set_sensitive(False)

        label = Gtk.Label(label=" ")
        self.show_button_box.pack_start(label, False, False, 0)

        vbox = Gtk.VBox(spacing=6)
        self.show_button_box.pack_start(vbox, False, False, 0)

        for item in desktop_icons:
            vbox.pack_start(DesktopIcon(item), False, False, 0)

        button = WidgetFactory.create("CheckButton",
                                      label=_("Show mounted volumes on desktop"),
                                      key="org.gnome.nautilus.desktop.volumes-visible",
                                      backend="gsettings")
        vbox.pack_start(button, False, False, 0)

        button = WidgetFactory.create("CheckButton",
                                      label=_('Show contents of "Home Folder" on desktop'),
                                      key="org.gnome.nautilus.preferences.desktop-is-home-dir",
                                      backend="gsettings")
        vbox.pack_start(button, False, False, 0)

    def on_show_button_changed(self, widget):
        self.show_button_box.set_sensitive(self.show_button.get_active())
