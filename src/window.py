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

import asyncio, re as regex
from gi.repository import Adw, Gtk, Gio, GLib, GObject
from .results import EchoResultsPage

from gettext import gettext
from icmplib import async_ping
from icmplib import (
    NameLookupError,
    SocketPermissionError,
    TimeExceeded,
    DestinationUnreachable,
    ICMPSocketError,
    SocketAddressError,
)


@Gtk.Template(resource_path="/io/github/lo2dev/Echo/window.ui")
class EchoWindow(Adw.ApplicationWindow):
    __gtype_name__ = "EchoWindow"

    main_view = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    address_bar = Gtk.Template.Child()
    spinner_revealer = Gtk.Template.Child()
    ping_buttons_stack = Gtk.Template.Child()

    ping_count_adjust = Gtk.Template.Child()
    ping_interval_adjust = Gtk.Template.Child()
    ping_timeout_adjust = Gtk.Template.Child()
    ping_source_row = Gtk.Template.Child()
    ping_family_row = Gtk.Template.Child()

    network_monitor = Gio.NetworkMonitor.get_default()
    network_available = GObject.Property(type=bool, default=True)

    payload_size = 56

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.network_monitor.connect("network-changed", self.on_network_changed)

        self.settings = Gio.Settings(schema_id="io.github.lo2dev.Echo")
        self.settings.bind(
            "width", self, "default-width", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "height", self, "default-height", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "ping-count", self.ping_count_adjust, "value", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "ping-interval",
            self.ping_interval_adjust,
            "value",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.settings.bind(
            "ping-timeout",
            self.ping_timeout_adjust,
            "value",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.settings.bind(
            "ping-source", self.ping_source_row, "text", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "ping-family",
            self.ping_family_row,
            "selected",
            Gio.SettingsBindFlags.DEFAULT,
        )

        self.notif = Gio.Notification()
        self.background_task = None

    @Gtk.Template.Callback()
    def cancel_ping(self, *_) -> None:
        self.background_task.cancel()

    @Gtk.Template.Callback()
    def ping(self, *_) -> None:
        address = self.address_bar.props.text

        if not address:
            return

        address = regex.sub(".+://|/+$", "", address)
        self.address_bar.props.text = address
        self.address_bar.remove_css_class("error")

        # TODO: maybe find a better way to check the family?
        # To avoid confusion: the int from `saved_family` corresponds to the ComboRow `selected` property.
        saved_family = self.settings.get_int("ping-family")
        ping_family = None
        if saved_family == 0:
            ping_family = None
        elif saved_family == 1:
            ping_family = 4
        elif saved_family == 2:
            ping_family = 6

        self.disable_form(True)

        self.background_task = asyncio.create_task(
            self.ping_task(
                address,
                count=self.settings.get_int("ping-count"),
                interval=self.settings.get_double("ping-interval"),
                timeout=self.settings.get_double("ping-timeout"),
                source=self.settings.get_string("ping-source"),
                family=ping_family,
                payload_size=self.payload_size,
                privileged=False,
            )
        )

        self.spinner_timeout = GLib.timeout_add_seconds(
            1, lambda: self.spinner_revealer.set_reveal_child(True)
        )

    async def ping_task(self, *args, **kwargs) -> None:
        self.notif.set_title(gettext("Ping Failed"))

        notif_icon = Gio.ThemedIcon(name="dialog-error-symbolic")
        self.notif.set_icon(notif_icon)

        try:
            result = await async_ping(*args, **kwargs)

            if result.is_alive:
                results_page = EchoResultsPage(result, self.address_bar.get_text(), self.payload_size)
                self.main_view.push(results_page)

                self.notif.set_title(gettext("Ping Succeeded"))
                self.notif.set_body(f"{self.address_bar.props.text}")

                notif_icon = Gio.ThemedIcon(name="emblem-ok-symbolic")
                self.notif.set_icon(notif_icon)
            else:
                error_text = f"{self.address_bar.get_text()} is unreachable"
                self.notif.set_body(error_text)
                self.ping_error(error_text)
        except NameLookupError:
            error_text = gettext("The host can't be resolved or doesn't exist")
            self.notif.set_body(error_text)
            self.ping_error(error_text)
        except SocketPermissionError:
            self.ping_error(
                gettext("Insufficient permissions"), is_insufficient_error=True
            )
        except TimeExceeded:
            error_text = gettext("Host timeout")
            self.notif.set_body(error_text)
            self.ping_error(error_text)
        except DestinationUnreachable:
            error_text = gettext("Destination is unreachable")
            self.notif.set_body(error_text)
            self.ping_error(error_text)
        except SocketAddressError:
            error_text = gettext("Cannot use source address")
            self.ping_error(error_text)
        except KeyboardInterrupt:
            # This is good actually!
            pass
        except Exception as error:
            self.notif.set_body(str(error))
            self.ping_error(str(error))
            print(error)
        finally:
            if not self.props.is_active:
                self.props.application.send_notification("ping-result", self.notif)

            self.disable_form(False)

    def ping_error(self, error_text, is_insufficient_error=False) -> None:
        toast = Adw.Toast(title=error_text, priority=Adw.ToastPriority.HIGH, timeout=0)

        # TODO: find a better way to deal with this edge case
        if is_insufficient_error:
            toast.set_button_label(gettext("Details"))
            toast.connect(
                "button-clicked",
                lambda x: Gio.AppInfo.launch_default_for_uri(
                    "https://github.com/lo2dev/Echo?tab=readme-ov-file#insufficient-permissions"
                ),
            )

        self.toast_overlay.add_toast(toast)

        self.main_view.connect("pushed", lambda x: toast.dismiss())

        self.address_bar.add_css_class("error")

    def disable_form(self, disable) -> None:
        if disable:
            self.address_bar.props.sensitive = False
            self.ping_buttons_stack.props.visible_child_name = "pinging"
        elif not disable:
            GLib.source_remove(self.spinner_timeout)
            self.spinner_revealer.props.reveal_child = False
            self.address_bar.props.sensitive = True

            self.ping_buttons_stack.props.visible_child_name = "not-pinging"

    def on_network_changed(self, _, network_available):
        self.network_available = network_available
