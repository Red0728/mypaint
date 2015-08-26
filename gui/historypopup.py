# This file is part of MyPaint.
# Copyright (C) 2009-2013 by Martin Renold <martinxyz@gmx.ch>
# Copyright (C) 2010-2015 by the MyPaint Development Team.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import gtk2compat
import gtk
from gtk import gdk

import cairo
from lib import helpers
import windowing


"""Color history popup."""


## Module constants

popup_height = 60
bigcolor_width = popup_height
smallcolor_width = popup_height/2


## Class definitions

class HistoryPopup(windowing.PopupWindow):
    outside_popup_timeout = 0

    def __init__(self, app, doc):
        windowing.PopupWindow.__init__(self, app)
        # TODO: put the mouse position onto the selected color
        self.set_position(gtk.WIN_POS_MOUSE)

        self.app = app
        self.app.kbm.add_window(self)

        hist_len = len(self.app.brush_color_manager.get_history())
        self.popup_width = bigcolor_width + (hist_len-1)*smallcolor_width

        self.set_events(gdk.BUTTON_PRESS_MASK |
                        gdk.BUTTON_RELEASE_MASK |
                        gdk.ENTER_NOTIFY |
                        gdk.LEAVE_NOTIFY
                        )
        self.connect("button-release-event", self.button_release_cb)
        self.connect("button-press-event", self.button_press_cb)

        self.connect("draw", self.draw_cb)

        self.set_size_request(self.popup_width, popup_height)

        # Selection index. Each enter() (i.e. keypress) advances this.
        self.selection = None

        self.doc = doc
        self._active = False

        model = app.doc.model
        model.sync_pending_changes += self._sync_pending_changes_cb

    def enter(self):
        self._active = True
        mgr = self.app.brush_color_manager
        hist = mgr.get_history()
        if self.selection is None:
            self.selection = len(hist) - 1
            color = mgr.get_color()
            if hist[self.selection] == color:
                self.selection -= 1
        else:
            self.selection = (self.selection - 1) % len(hist)

        mgr.set_color(hist[self.selection])

        # popup placement
        x, y = self.get_position()
        bigcolor_center_x = self.selection * smallcolor_width + bigcolor_width/2
        self.move(x + self.popup_width/2 - bigcolor_center_x, y + bigcolor_width)
        self.show_all()

        self.get_window().set_cursor(gdk.Cursor(gdk.CROSSHAIR))

    def leave(self, reason):
        self.hide()
        self._active = False

    def button_press_cb(self, widget, event):
        pass

    def button_release_cb(self, widget, event):
        pass

    def _sync_pending_changes_cb(self, model, **kwargs):
        if self._active:
            return
        self.selection = None

    def draw_cb(self, widget, cr):
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.paint()

        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        cr.translate(0.0, popup_height/2.0)

        hist = self.app.brush_color_manager.get_history()
        for i, c in enumerate(hist):
            if i != self.selection:
                cr.scale(0.5, 0.5)

            line_width = 3.0
            distance = 2*line_width
            rect = [0, -popup_height/2.0, popup_height, popup_height]
            rect[0] += distance/2.0
            rect[1] += distance/2.0
            rect[2] -= distance
            rect[3] -= distance
            cr.rectangle(*rect)
            cr.set_source_rgb(*c.get_rgb())
            cr.fill_preserve()
            cr.set_line_width(line_width)
            cr.set_source_rgb(0, 0, 0)
            cr.stroke()
            cr.translate(popup_height, 0)

            if i != self.selection:
                cr.scale(2.0, 2.0)

        return True
