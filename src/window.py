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

from gi.repository import Adw, Gtk, Gio, GLib
from .results import EchoResultsPage

import sys
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
    address_spinner = Gtk.Template.Child()
    ping_button = Gtk.Template.Child()
    cancel_ping_button = Gtk.Template.Child()
    network_error_banner = Gtk.Template.Child()

    ping_options = Gtk.Template.Child()
    ping_count_adjust = Gtk.Template.Child()
    ping_interval_adjust = Gtk.Template.Child()
    ping_timeout_adjust = Gtk.Template.Child()
    ping_source_row = Gtk.Template.Child()
    ping_family_row = Gtk.Template.Child()


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
        self.settings.bind("ping-options-expanded", self.ping_options, "expanded", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-count", self.ping_count_adjust, "value", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-interval", self.ping_interval_adjust, "value", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-timeout", self.ping_timeout_adjust, "value", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-source", self.ping_source_row, "text", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("ping-family", self.ping_family_row, "selected", Gio.SettingsBindFlags.DEFAULT)

        self.address_bar.connect("entry-activated", self.ping)
        self.ping_button.connect("clicked", self.ping)
        self.cancel_ping_button.connect("clicked", self.cancel_ping)

        # The box parent creates an unwanted subtle margin in the address bar
        # so we hide and show the box instead of spinner
        self.spinner_parent = self.address_spinner.get_parent()
        self.spinner_parent.set_visible(False)

        # This gets the GtkRevealer containing the children
        self.ping_options_children = self.ping_options.get_child().get_last_child()

    def cancel_ping(self, *_):
        if self.task:
            self.cancel_ping_button.set_sensitive(False)
            self.cancel_ping_button.set_label(gettext("Cancelling Ping"))

            self.task.killed = True
            self.task = None

    def ping(self, *_):
        address = self.address_bar.get_text()

        if address == "":
            self.ping_error(gettext("Enter a host to ping"), False)
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

        self.disable_form(True)

        self.task = ThreadWithTrace(
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

        self.task.daemon = True
        self.task.start()

        self.spinner_timeout = GLib.timeout_add_seconds(1, lambda: self.spinner_parent.set_visible(True))

    def ping_task(self, *args, **kwargs):
        try:
            result = ping(*args, **kwargs)

            if result.is_alive:
                results_page = EchoResultsPage(result, self.address_bar.get_text())
                if self.task and not self.task.killed:
                    self.main_view.push(results_page)
            else:
                self.ping_error(f"{self.address_bar.get_text()} is unreachable", False)
        except NameLookupError:
            self.ping_error(gettext("The host can't be resolved or doesn't exist"), False)
        except SocketPermissionError:
            self.ping_error(gettext("Insufficient permissions"), True)
        except TimeExceeded:
            self.ping_error(gettext("Host timeout"), False)
        except DestinationUnreachable:
            self.ping_error(gettext("Destination is unreachable"), False)
        except KeyboardInterrupt:
            # This is good actually!
            pass
        except:
            self.ping_error(gettext("Unexpected error"), False)

        self.disable_form(False)

    def ping_error(self, error_text, is_insufficient_error):
        toast = Adw.Toast()
        toast.set_title(error_text)
        toast.set_priority(Adw.ToastPriority.HIGH)

        # TODO: find a better way to deal with this edge case
        if is_insufficient_error:
            toast.set_button_label(gettext("Details"))
            toast.connect("button-clicked", lambda x: Gio.AppInfo.launch_default_for_uri("https://github.com/lo2dev/Echo?tab=readme-ov-file#insufficient-permissions"))

        self.toast_overlay.add_toast(toast)

        self.main_view.connect("pushed", lambda x: toast.dismiss())

        self.address_bar.add_css_class("error")

    def disable_form(self, disable):
        if disable == True:
            self.ping_button.set_sensitive(False)
            self.address_bar.set_sensitive(False)
            self.ping_options_children.set_sensitive(False)

            self.ping_button.set_visible(False)
            self.cancel_ping_button.set_visible(True)
        elif disable == False:
            GLib.source_remove(self.spinner_timeout)
            self.spinner_parent.set_visible(False)
            self.ping_button.set_sensitive(True)
            self.address_bar.set_sensitive(True)
            self.ping_options_children.set_sensitive(True)

            self.ping_button.set_visible(True)
            self.cancel_ping_button.set_visible(False)
            self.cancel_ping_button.set_sensitive(True)
            self.cancel_ping_button.set_label(gettext("Cancel Ping"))

# Hacky way to kill a thread.
# TODO: find a better way to kill a thread
# Reference: https://web.archive.org/web/20130503082442/http://mail.python.org/pipermail/python-list/2004-May/281943.html
class ThreadWithTrace(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.killed = False

    def start(self):
        if self.killed:
            return
        self.__run_backup = self.run
        self.run = self.__run
        super().start()

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise KeyboardInterrupt
        return self.localtrace

    def kill(self):
        self.killed = True

