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

from gi.repository import Adw, Gtk
from gettext import gettext
from .results_card import EchoResultsCard


@Gtk.Template(resource_path="/io/github/lo2dev/Echo/results.ui")
class EchoResultsPage(Adw.NavigationPage):
    __gtype_name__ = "EchoResultsPage"

    results_icon = Gtk.Template.Child()
    result_title = Gtk.Template.Child()
    address_ip = Gtk.Template.Child()

    stat_cards_box = Gtk.Template.Child()

    logs_list = Gtk.Template.Child()
    packets_sent = Gtk.Template.Child()
    packets_received = Gtk.Template.Child()
    packet_loss = Gtk.Template.Child()

    def __init__(self, result_data, result_title, payload_size, **kwargs):
        super().__init__(**kwargs)

        self.result_title.props.label = str(result_title)

        for idx, packet in enumerate(result_data.rtts):
            self.logs_list.append(
                Adw.ActionRow(
                    icon_name="arrow-pointing-away-from-line-down-symbolic",
                    title=f"{gettext("Packet")} {idx + 1}",
                    subtitle=f"{payload_size} bytes, {packet:.2f} ms",
                    subtitle_selectable=True,
                    css_classes=["property"]
                )
            )

        if result_title == result_data.address:
            self.address_ip.props.visible = False
        else:
            self.address_ip.props.visible = True
            self.address_ip.props.label = str(result_data.address)

        min_card = EchoResultsCard(gettext("Minimum"), f"{result_data.min_rtt:.1f}")
        avg_card = EchoResultsCard(gettext("Average"), f"{result_data.avg_rtt:.1f}")
        max_card = EchoResultsCard(gettext("Maximum"), f"{result_data.max_rtt:.1f}")
        self.stat_cards_box.append(min_card)
        self.stat_cards_box.append(avg_card)
        self.stat_cards_box.append(max_card)

        self.packets_sent.props.subtitle = str(result_data.packets_sent)
        self.packets_received.props.subtitle = str(result_data.packets_received)
        self.packet_loss.props.subtitle = f"{result_data.packet_loss:.0%}"
