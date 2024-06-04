# window.py
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

from gi.repository import Adw, Gtk, Gio
from .results import EchoResultsPage

import threading
from icmplib import ping, NameLookupError

@Gtk.Template(resource_path='/io/github/lo2dev/Echo/window.ui')
class EchoWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'EchoWindow'

    main_view = Gtk.Template.Child()
    address_bar = Gtk.Template.Child()
    ping_button = Gtk.Template.Child()
    ping_error_label = Gtk.Template.Child()
    network_error_banner = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        network_monitor = Gio.NetworkMonitor.get_default()
        print(network_monitor.get_network_available())
        self.network_error_banner.set_revealed(not network_monitor.get_network_available())

        self.settings = Gio.Settings(schema_id="io.github.lo2dev.Echo")
        self.settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)
        self.ping_button.connect("clicked", self.ping)

    def ping(self, *_):
        address = self.address_bar.get_text()

        if address == "":
            self.ping_error("Enter a host to ping")
            return
        else:
            self.ping_error_label.set_visible(False)
            self.address_bar.remove_css_class("error")

        self.ping_button.set_sensitive(False)
        self.address_bar.set_sensitive(False)
        self.ping_button.set_label("Pinging")

        task = threading.Thread(
            target=self.ping_task,
            args=(address,),
            kwargs={"count": 4, "family": None, "privileged": False}
            )

        task.start()

    def ping_task(self, *args, **kwargs):
        try:
            result = ping(*args, **kwargs)

            if result.is_alive:
                results_page = EchoResultsPage(result, self.address_bar.get_text())
                self.main_view.push(results_page)
            else:
                self.ping_error(f"{self.address_bar.get_text()} is unreachable")
        except NameLookupError:
            self.ping_error(f"{self.address_bar.get_text()} is unreachable")

        self.ping_button.set_sensitive(True)
        self.address_bar.set_sensitive(True)
        self.ping_button.set_label("Ping")

    def ping_error(self, error_text):
        self.ping_error_label.set_text(error_text)
        self.ping_error_label.set_visible(True)
        self.address_bar.add_css_class("error")

