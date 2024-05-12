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

import asyncio, threading
from icmplib import async_ping

@Gtk.Template(resource_path='/io/github/lo2dev/Echo/window.ui')
class EchoWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'EchoWindow'

    adress_bar = Gtk.Template.Child()
    label = Gtk.Template.Child()
    ping_button = Gtk.Template.Child()

    def start_asyncio_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def start_thread(self):
        threading.Thread(target=self.start_asyncio_loop).start()
        self.async_task()

    def async_task(self):
        async def ping():
            adress = self.adress_bar.get_text()
            host = await async_ping(adress, count=5, privileged=False)

            print(host)

        asyncio.run(ping())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ping_button.connect("clicked", self.start_thread)

