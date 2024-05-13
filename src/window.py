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
from icmplib import ping

@Gtk.Template(resource_path='/io/github/lo2dev/Echo/window.ui')
class EchoWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'EchoWindow'

    address_bar = Gtk.Template.Child()
    ping_button = Gtk.Template.Child()
    result_title = Gtk.Template.Child()
    stats = Gtk.Template.Child()
    packet_loss_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ping_button.connect("clicked", self.ping)
        self.address_bar.connect("activate", self.ping)

    def ping(self, *_):
        address = self.address_bar.get_text()
        task = threading.Thread(
            target=self.ping_task,
            args=(address,),
            kwargs={"count": 1, "privileged": False}
            )

        task.start()

    def ping_task(self, *args, **kwargs):
        result = ping(*args, **kwargs)

        self.result_title.set_visible(True)
        self.stats.set_visible(True)

        if result.is_alive:
            self.result_title.set_text(f"{result.address} is alive")
            self.result_title.add_css_class("success")

            if result.packets_sent == 1:
                self.stats.set_text(f"Response time (ms): {result.avg_rtt}")
            else:
                self.stats.set_text(f"Response time (ms): min {result.min_rtt} / avg {result.avg_rtt} / max {result.max_rtt}")

            self.packet_loss_label.set_text(f"{format(result.packet_loss, '.2%')} packet loss")
        else:
            self.result_title.set_text(f"{result.address} is unreachable")
            self.result_title.add_css_class("error")

