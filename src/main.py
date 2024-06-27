# main.py
#
# Copyright 2024 Lo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import EchoWindow


class EchoApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.lo2dev.Echo',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action(
            "close",
            lambda *_: window.close() if (window := self.get_active_window()) else None,
            ("<primary>w",),
        )
        self.create_action('about', self.on_about_action)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = EchoWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        about = Adw.AboutDialog.new_from_appdata(
            "/io/github/lo2dev/Echo/io.github.lo2dev.Echo.metainfo.xml"
        )
        about.set_copyright("© 2024 Lo")
        about.present(self.props.active_window)

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    app = EchoApplication()
    return app.run(sys.argv)

