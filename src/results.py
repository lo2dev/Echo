# results.py
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

@Gtk.Template(resource_path='/io/github/lo2dev/Echo/results.ui')
class EchoResultsPage(Adw.NavigationPage):
    __gtype_name__ = 'EchoResultsPage'

    results_icon = Gtk.Template.Child()
    result_title = Gtk.Template.Child()
    address_ip = Gtk.Template.Child()
    response_time = Gtk.Template.Child()
    packets_sent = Gtk.Template.Child()
    packets_received = Gtk.Template.Child()
    packet_loss = Gtk.Template.Child()

    def __init__(self, result_data, result_title, **kwargs):
        super().__init__(**kwargs)

        self.result_title.props.label = str(result_title)
        self.address_ip.props.label = str(result_data.address)
        self.response_time.props.subtitle = f"min {result_data.min_rtt:.1f} ⸱ avg {result_data.avg_rtt:.1f} ⸱ max {result_data.max_rtt:.1f} ms"
        self.packets_sent.props.subtitle = str(result_data.packets_sent)
        self.packets_received.props.subtitle = str(result_data.packets_received)
        self.packet_loss.props.subtitle = f"{result_data.packet_loss:.0%}"

