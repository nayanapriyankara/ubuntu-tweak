#!/usr/bin/env python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
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

import pygtk
pygtk.require("2.0")
import os
import gtk
import gconf
import gobject
import gettext
import time
import cairo
from Settings import *

class Colleague:
    def __init__(self, mediator):
        self.mediator = mediator

    def state_changed(self, widget, data = None):
        self.mediator.colleague_changed()

class Mediator:
    def colleague_changed(self):
        pass

class GconfCheckButton(gtk.CheckButton, BoolSetting):
    def __init__(self, label, key):
        gtk.CheckButton.__init__(self)
        BoolSetting.__init__(self, key)

        self.set_label(label)
        self.set_active(self.get_bool())

        self.client.notify_add(key, self.value_changed)
        self.connect("toggled", self.button_toggled)

    def value_changed(self, client, id, entry, data = None):
        self.set_active(self.get_bool())

    def button_toggled(self, widget, data = None):
        self.client.set_bool(self.key, self.get_active())
        
class StrGconfCheckButton(GconfCheckButton, Colleague):
    def __init__(self, label, key, mediator):
        GconfCheckButton.__init__(self, label, key)
        Colleague.__init__(self, mediator)

        self.connect("toggled", self.state_changed)

    def button_toggled(self, widget, data = None):
        pass

class GconfEntry(gtk.Entry, StringSetting):
    def __init__(self, key):
        gtk.Entry.__init__(self)
        StringSetting.__init__(self, key)

        if self.get_string():
            self.set_text(self.get_string())
        else:
            self.set_text(_("Unset"))

        self.connect("activate", self.on_edit_finished_cb)
    
    def on_edit_finished_cb(self, widget, data = None):
        string = self.get_text()
        if string:
            self.client.set_string(self.key, self.get_text())
        else:
            self.client.unset(self.key)
            self.set_text(_("Unset"))

class CGconfCheckButton(GconfCheckButton, Colleague):
    def __init__(self, label, key, mediator):
        GconfCheckButton.__init__(self, label, key)
        Colleague.__init__(self, mediator)

        self.connect("toggled", self.state_changed)

class ColleagueCheckButton(gtk.CheckButton, Colleague):
    def __init__(self, label, mediator):
        gtk.CheckButton.__init__(self, label)
        Colleague.__init__(self, mediator)

        self.connect("toggled", self.state_changed)

class GconfCombobox(ConstStringSetting):
    def __init__(self, key, texts, values):
        ConstStringSetting.__init__(self, key, values)

        self.combobox = gtk.combo_box_new_text()
        self.texts = texts

        for text in texts:
            self.combobox.append_text(text)

        if self.get_string() in values:
            self.combobox.set_active(values.index(self.get_string()))

        self.combobox.connect("changed", self.value_changed_cb)

    def value_changed_cb(self, widget, data = None):
        text = widget.get_active_text()
        self.client.set_string(self.key, self.values[self.texts.index(text)])

class GconfScale(NumSetting, gtk.HScale):
    def __init__(self, min, max, key, digits = 0):
        gtk.HScale.__init__(self)
        Setting.__init__(self, key)
        
        self.set_range(min, max)
        self.set_digits(digits)
        self.set_value_pos(gtk.POS_RIGHT)
        self.connect("value-changed", self.on_value_changed)

        self.set_value(self.get_num())

    def on_value_changed(self, widget, data = None):
        self.set_num(widget.get_value())


class EntryBox(gtk.HBox):
    def __init__(self, label, text):
        gtk.HBox.__init__(self)

        label = gtk.Label(label)
        self.pack_start(label, False, False,10)
        entry = gtk.Entry()
        if text: entry.set_text(text)
        entry.set_editable(False)
        entry.set_size_request(300, -1)
        self.pack_end(entry, False, False, 0)

class HScaleBox(gtk.HBox):

    def hscale_value_changed_cb(self, widget, data = None):
        client = gconf.client_get_default()
        value = client.get(data)
        if value.type == gconf.VALUE_INT:
            client.set_int(data, int(widget.get_value()))
        elif value.type == gconf.VALUE_FLOAT:
            client.set_float(data, widget.get_value())

    def __init__(self, label, min, max, key, digits = 0):
        gtk.HBox.__init__(self)
        self.pack_start(gtk.Label(label), False, False, 0)
        
        hscale = gtk.HScale()
        hscale.set_size_request(150, -1)
        hscale.set_range(min, max)
        hscale.set_digits(digits)
        hscale.set_value_pos(gtk.POS_RIGHT)
        self.pack_end(hscale, False, False, 0)
        hscale.connect("value-changed", self.hscale_value_changed_cb, key)

        client = gconf.client_get_default()
        value = client.get(key)

        if value:
            if value.type == gconf.VALUE_INT:
                hscale.set_value(client.get_int(key))
            elif value.type == gconf.VALUE_FLOAT:
                hscale.set_value(client.get_float(key))


class ComboboxItem(gtk.HBox):

    def __init__(self, label, texts, values, key):
        gtk.HBox.__init__(self)
        self.pack_start(gtk.Label(label), False, False, 0)    

        combobox = gtk.combo_box_new_text()
        combobox.texts = texts
        combobox.values = values
        combobox.connect("changed", self.value_changed_cb, key)
        self.pack_end(combobox, False, False, 0)

        for element in texts:
            combobox.append_text(element)

        client = gconf.client_get_default()

        if client.get_string(key) in values:
            combobox.set_active(values.index(client.get_string(key)))
    def value_changed_cb(self, widget, data = None):
        client = gconf.client_get_default()
        text = widget.get_active_text()
        client.set_string(data, widget.values[widget.texts.index(text)]) 

"""Popup and KeyGrabber come from ccsm"""
KeyModifier = ["Shift", "Control", "Mod1", "Mod2", "Mod3", "Mod4",
               "Mod5", "Alt", "Meta", "Super", "Hyper", "ModeSwitch"]

class Popup (gtk.Window):
    def __init__ (self, parent, text=None, child=None, decorated=True, mouse=False, modal=True):
        gtk.Window.__init__ (self, gtk.WINDOW_TOPLEVEL)
        self.set_type_hint (gtk.gdk.WINDOW_TYPE_HINT_UTILITY)
        self.set_position (mouse and gtk.WIN_POS_MOUSE or gtk.WIN_POS_CENTER_ALWAYS)
        if parent:
            self.set_transient_for (parent.get_toplevel ())
        self.set_modal (modal)
        self.set_decorated (decorated)
        self.set_title("")
        if text:
            label = gtk.Label (text)
            align = gtk.Alignment ()
            align.set_padding (20, 20, 20, 20)
            align.add (label)
            self.add (align)
        elif child:
            self.add (child)
        while gtk.events_pending ():
            gtk.main_iteration ()


    def destroy (self):
        gtk.Window.destroy (self)
        while gtk.events_pending ():
            gtk.main_iteration ()

class KeyGrabber (gtk.Button):

    __gsignals__ = {"changed" : (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            [gobject.TYPE_INT, gobject.TYPE_INT]),
                    "current-changed" : (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            [gobject.TYPE_INT, gobject.TYPE_INT])}

    key     = 0
    mods    = 0
    handler = None
    popup   = None

    label   = None

    def __init__ (self, parent = None, key = 0, mods = 0, label = None):
        '''Prepare widget'''
        super (KeyGrabber, self).__init__ ()

        self.main_window = parent
        self.key = key
        self.mods = mods

        self.label = label

        self.connect ("clicked", self.begin_key_grab)
        self.set_label ()

    def begin_key_grab (self, widget):
        self.add_events (gtk.gdk.KEY_PRESS_MASK)
        self.popup = Popup (self.main_window, _("Please press the new key combination"))
        self.popup.show_all()
        self.handler = self.popup.connect ("key-press-event",
                           self.on_key_press_event)
        while gtk.gdk.keyboard_grab (self.popup.window) != gtk.gdk.GRAB_SUCCESS:
            time.sleep (0.1)

    def end_key_grab (self):
        gtk.gdk.keyboard_ungrab (gtk.get_current_event_time ())
        self.popup.disconnect (self.handler)
        self.popup.destroy ()

    def on_key_press_event (self, widget, event):
        mods = event.state & gtk.accelerator_get_default_mod_mask ()

        if event.keyval in (gtk.keysyms.Escape, gtk.keysyms.Return) \
            and not mods:
            if event.keyval == gtk.keysyms.Escape:
                self.emit ("changed", self.key, self.mods)
            self.end_key_grab ()
            self.set_label ()
            return

        key = gtk.gdk.keyval_to_lower (event.keyval)
        if (key == gtk.keysyms.ISO_Left_Tab):
            key = gtk.keysyms.Tab

        if gtk.accelerator_valid (key, mods) \
            or (key == gtk.keysyms.Tab and mods):
            self.set_label (key, mods)
            self.end_key_grab ()
            self.key = key
            self.mods = mods
            self.emit ("changed", self.key, self.mods)
            return

        self.set_label (key, mods)

    def set_label (self, key = None, mods = None):
        if self.label:
            if key != None and mods != None:
                self.emit ("current-changed", key, mods)
            gtk.Button.set_label (self, self.label)
            return
        if key == None and mods == None:
            key = self.key
            mods = self.mods
        label = gtk.accelerator_name (key, mods)
        if not len (label):
            label = _("Disabled")
        gtk.Button.set_label (self, label)
