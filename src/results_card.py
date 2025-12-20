# results_card.py
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

from gi.repository import Gtk


@Gtk.Template(resource_path="/io/github/lo2dev/Echo/results_card.ui")
class EchoResultsCard(Gtk.Box):
    __gtype_name__ = "EchoResultsCard"

    card_title_label = Gtk.Template.Child()
    card_value_label = Gtk.Template.Child()

    def __init__(self, card_title, value, **kwargs):
        super().__init__(**kwargs)

        self.card_title_label.props.label = card_title
        self.card_value_label.props.label = value
