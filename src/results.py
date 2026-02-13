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

from gi.repository import Adw, Gtk, GObject
from gettext import gettext
from .results_card import ResultsCard


@Gtk.Template(resource_path="/io/github/lo2dev/Echo/results.ui")
class EchoResultsPage(Adw.NavigationPage):
    __gtype_name__ = "EchoResultsPage"

    result_title = GObject.Property(type=str)
    address_ip = Gtk.Template.Child()

    logs_list = Gtk.Template.Child()

    min_time = GObject.Property(type=str)
    avg_time = GObject.Property(type=str)
    max_time = GObject.Property(type=str)

    packets_sent = GObject.Property(type=str)
    packets_received = GObject.Property(type=str)
    packet_loss = GObject.Property(type=str)
    jitter = GObject.Property(type=str)

    def __init__(self, result_data, result_title, payload_size, **kwargs):
        super().__init__(**kwargs)

        self.result_title = result_title

        for idx, packet in enumerate(result_data.rtts):
            self.logs_list.append(
                Adw.ActionRow(
                    icon_name="arrow-pointing-away-from-line-down-symbolic",
                    title=f"{gettext('Packet')} {idx + 1}",
                    subtitle=f"{payload_size} bytes, {packet:.2f} ms",
                    subtitle_selectable=True,
                    css_classes=["property"]
                )
            )

        self.address_ip.props.label = str(result_data.address)
        if self.result_title == result_data.address:
            self.address_ip.props.visible = False

        self.min_time = f"{result_data.min_rtt:.1f}"
        self.avg_time = f"{result_data.avg_rtt:.1f}"
        self.max_time = f"{result_data.max_rtt:.1f}"

        self.packets_sent = result_data.packets_sent
        self.packets_received = result_data.packets_received
        self.packet_loss = f"{result_data.packet_loss:.0%}"
        self.jitter = f"{result_data.jitter:.1f} ms"

