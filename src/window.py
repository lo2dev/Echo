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

from gi.repository import Adw
from gi.repository import Gtk

import threading
from icmplib import ping, NameLookupError

@Gtk.Template(resource_path='/io/github/lo2dev/Echo/window.ui')
class EchoWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'EchoWindow'

    address_bar = Gtk.Template.Child()
    ping_button = Gtk.Template.Child()

    stack = Gtk.Template.Child()

    results_icon = Gtk.Template.Child()
    results = Gtk.Template.Child()
    stats = Gtk.Template.Child()
    result_title = Gtk.Template.Child()
    address_ip = Gtk.Template.Child()
    response_time = Gtk.Template.Child()
    packets_sent = Gtk.Template.Child()
    packets_received = Gtk.Template.Child()
    packet_loss = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ping_button.connect("clicked", self.ping)
        self.address_bar.connect("activate", self.ping)

    def ping(self, *_):
        address = self.address_bar.get_text()
        self.ping_button.set_sensitive(False)
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
                self.results_icon.set_from_icon_name("emblem-default-symbolic")
                self.results_icon.set_css_classes(["success"])

                self.result_title.set_text(f"{self.address_bar.get_text()} is alive")
                self.address_ip.set_text(f"{result.address}")
                self.result_title.set_css_classes(["success", "title-3"])

                self.stats.set_visible(True)
                self.response_time.set_subtitle(f"min {result.min_rtt} / avg {result.avg_rtt} / max {result.max_rtt}")

                self.packets_sent.set_subtitle(f"{result.packets_sent}")
                self.packets_received.set_subtitle(f"{result.packets_received}")
                self.packet_loss.set_subtitle(f"{format(result.packet_loss, '.2%')}")
            else:
                self.result_error()
        except NameLookupError:
            self.result_error()

        self.ping_button.set_sensitive(True)
        self.ping_button.set_label("Ping")
        self.stack.set_visible_child(self.results)

    def result_error(self):
        self.results_icon.set_from_icon_name("dialog-error-symbolic")
        self.results_icon.set_css_classes(["error"])
        self.address_ip.set_text("")

        self.stats.set_visible(False)

        self.result_title.set_text(f"{self.address_bar.get_text()} is unreachable")
        self.result_title.set_css_classes(["error", "title-3"])

