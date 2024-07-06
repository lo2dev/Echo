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

import threading, re as regex
from gettext import gettext
from icmplib import ping
from icmplib import NameLookupError, SocketPermissionError, TimeExceeded, DestinationUnreachable

@Gtk.Template(resource_path='/io/github/lo2dev/Echo/window.ui')
class EchoWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'EchoWindow'

    main_view = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    address_bar = Gtk.Template.Child()
    ping_button = Gtk.Template.Child()
    network_error_banner = Gtk.Template.Child()

    advanced_options = Gtk.Template.Child()
    ping_count_adjust = Gtk.Template.Child()
    ping_interval_adjust = Gtk.Template.Child()
    ping_timeout_adjust = Gtk.Template.Child()
    ping_source_row = Gtk.Template.Child()
    ping_family_row = Gtk.Template.Child()

    # TODO: add a class variable which will hold the address inputed by the user.
    # the current method breaks if the user deletes the input from the address bar before the result is shown

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # NOTE: NetworkMonitor doesn't work for some reason
        # network_monitor = Gio.NetworkMonitor.get_default()
        # print(network_monitor.get_network_available())
        # self.network_error_banner.set_revealed(not network_monitor.get_network_available())

        self.settings = Gio.Settings(schema_id="io.github.lo2dev.Echo")
        self.settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("advanced-options-expanded", self.advanced_options, "expanded", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-count", self.ping_count_adjust, "value", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-interval", self.ping_interval_adjust, "value", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-timeout", self.ping_timeout_adjust, "value", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-source", self.ping_source_row, "text", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-family", self.ping_family_row, "selected", Gio.SettingsBindFlags.DEFAULT)

        self.address_bar.connect("entry-activated", self.ping)
        self.ping_button.connect("clicked", self.ping)

    def ping(self, *_):
        address = self.address_bar.get_text()

        if address == "":
            self.ping_error(gettext("Enter a host to ping"))
            return
        else:
            self.address_bar.remove_css_class("error")

        address = regex.sub("^(http|https)://|/+$", "", address)
        self.address_bar.set_text(address)

        # TODO: maybe find a better way to check the family?
	    # To avoid confusion: the int from `saved_family` corresponds to the ComboRow `selected` property.
        saved_family = self.settings.get_int("ping-family")
        ping_family = None;
        if saved_family == 0:
            ping_family = None
        elif saved_family == 1:
            ping_family = 4
        elif saved_family == 2:
            ping_family = 6

        self.ping_button.set_sensitive(False)
        self.address_bar.set_sensitive(False)
        self.advanced_options.set_sensitive(False)
        self.ping_button.set_label(gettext("Pinging"))

        task = threading.Thread(
            target=self.ping_task,
            args=(address,),
            kwargs={
                "count": self.settings.get_int("ping-count"),
                "interval": self.settings.get_double("ping-interval"),
                "timeout": self.settings.get_double("ping-timeout"),
                "source": self.settings.get_string("ping-source"),
                "family": ping_family,
                "privileged": False
                }
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
            self.ping_error(gettext("The host can't be resolved or doesn't exist"))
        except SocketPermissionError:
            self.ping_error(gettext("Insufficient permissions"))
        except TimeExceeded:
            self.ping_error(gettext("Host timeout"))
        except DestinationUnreachable:
            self.ping_error(gettext("Destination is unreachable"))
        except:
            self.ping_error(gettext("Unexpected error"))


        self.ping_button.set_sensitive(True)
        self.address_bar.set_sensitive(True)
        self.advanced_options.set_sensitive(True)
        self.ping_button.set_label(gettext("Ping"))

    def ping_error(self, error_text):
        toast = Adw.Toast()
        toast.set_title(error_text)
        toast.set_priority(Adw.ToastPriority.HIGH)
        self.toast_overlay.add_toast(toast)

        self.main_view.connect("pushed", lambda x: toast.dismiss())

        self.address_bar.add_css_class("error")

