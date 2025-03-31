#!/usr/bin/env python3

import subprocess
import threading
import gi  # type: ignore
gi.require_version('Gtk', '3.0')
import glob
import os
from pathlib import Path
from datetime import datetime
from gi.repository import Gtk, GLib, Gdk, Pango # type: ignore
from utils.logger import LogLevel, Logger
from tools.hyprland import get_hyprland_startup_apps, toggle_hyprland_startup
from tools.globals import get_current_session
from tools.swaywm import get_sway_startup_apps, toggle_sway_startup

class AutostartTab(Gtk.Box):
    """Autostart settings tab"""

    def __init__(self, logging: Logger):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # add css
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        row {
            padding: 8px;
            border-bottom: 1px solid alpha(@theme_fg_color, 0.1);
        }
        row:selected {
            background-color: alpha(@theme_selected_bg_color, 0.1);
        }
        .app-row {
            border-radius: 6px;
            margin: 2px 4px;
        }
        .app-row:hover {
            background-color: alpha(@theme_fg_color, 0.05);
        }
        .toggle-button {
            min-width: 80px;
            border-radius: 4px;
        }
        .toggle-button.enabled {
            background: alpha(@accent_color, 0.9);
            color: @theme_selected_fg_color;
        }
        .toggle-button.disabled {
            background: @theme_selected_bg_color;
            color: @theme_selected_fg_color;
        }
        .app-label {
            margin: 0 8px;
            font-size: 1.1em;
        }
        """)
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        
        self.logging = logging
        self.startup_apps = {}
        
        self.update_timeout_id = None
        self.update_interval = 100  # in ms
        self.is_visible = False

        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_hexpand(True)
        self.set_vexpand(True)
        hypr_apps = get_hyprland_startup_apps()
        if not hypr_apps:
            logging.log(LogLevel.Warn, f"failed to get hyprland config")
        
        # Create header box with title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Add display icon
        display_icon = Gtk.Image.new_from_icon_name(
            "system-run-symbolic", Gtk.IconSize.DIALOG
        )
        title_box.pack_start(display_icon, False, False, 0)

        # Add title
        display_label = Gtk.Label()
        display_label.set_markup(
            "<span weight='bold' size='large'>Autostart Settings</span>"
        )
        display_label.set_halign(Gtk.Align.START)
        title_box.pack_start(display_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)
        
        # Add scan button 
        self.scan_button = Gtk.Button()
        scan_icon = Gtk.Image.new_from_icon_name(
            "view-refresh-symbolic", Gtk.IconSize.BUTTON
        )
        self.scan_button.set_image(scan_icon)
        self.scan_button.set_tooltip_text("Rescan autostart apps")
        self.scan_button.connect("clicked", self.on_scan_clicked)
        self.scan_button.set_visible(True)
        header_box.pack_end(self.scan_button, False, False, 0)

        self.pack_start(header_box, False, False, 0)
        
        if get_current_session() == "Hyprland":
            # Add session info
            session_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)     
            session_label = Gtk.Label(label="Session: {}".format(get_current_session())+ "\nKeep your autostart.conf at: ~/.config/hypr/autostart.conf" )
            session_box.pack_start(session_label, False, False, 0)
            self.pack_start(session_box, False, True, 0)
        if get_current_session() == "sway":
            # Add session info
            session_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)     
            session_label = Gtk.Label(label="Session: {}".format(get_current_session())+ "\nKeep your autostart.conf at: ~/.config/sway/autostart.conf" )
            session_box.pack_start(session_label, False, False, 0)
            self.pack_start(session_box, False, True, 0)
        
        # Add toggle switches box
        toggles_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        toggles_box.set_margin_top(5)
        toggles_box.set_margin_bottom(2)
        
        # toggle to shows system autostart apps
        toggle1_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toggle1_label = Gtk.Label(label="Show system autostart apps")
        toggle1_label.set_halign(Gtk.Align.START)
        self.toggle1_switch = Gtk.Switch()
        self.toggle1_switch.set_active(False)
        self.toggle1_switch.connect("notify::active", self.on_toggle1_changed)
        toggle1_box.pack_start(toggle1_label, False, False, 0)
        toggle1_box.pack_start(self.toggle1_switch, False, False, 0)
        
        # Add  toggle boxe to the main toggle box
        toggles_box.pack_start(toggle1_box, False, False, 0)
        
        # Add separator line
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(5)
        separator.set_margin_bottom(5)
        
        # Add toggle box to main container
        self.pack_start(toggles_box, False, False, 0)
        self.pack_start(separator, False, False, 0)
        
        # Add listbox for autostart apps
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_window.add(self.listbox)
        self.pack_start(scrolled_window, True, True, 0)
        
        # Initial population
        self.refresh_list()
        
        # Set up timer check for external changes
        GLib.timeout_add(4000, self.check_external_changes)
        
        self.connect("realize", self.on_realize)
        
    def on_realize(self, widget):
        GLib.idle_add(self.refresh_list)
    
    def on_toggle1_changed(self, switch, gparam):
        """Handle toggle for system autostart apps"""
        show_system = switch.get_active()
        self.logging.log(LogLevel.Info, f"Show system autostart apps: {show_system}")
        self.refresh_list()
        
    
    def get_startup_apps(self):
        autostart_dirs = [
            Path.home() / ".config/autostart"
        ]
        
        # Add system directories
        if hasattr(self, 'toggle1_switch') and self.toggle1_switch.get_active():
            autostart_dirs.extend([
                Path("/etc/xdg/autostart"),
            ])
    
        startup_apps = {}
    
        for autostart_dir in autostart_dirs:
            if autostart_dir.exists():
                for desktop_file in glob.glob(str(autostart_dir / "*.desktop")):
                    if desktop_file.endswith(".desktop.disabled"):
                        continue
                        
                    app_name = os.path.basename(desktop_file).replace(".desktop", "")
                    
                    is_hidden = False
                    try:
                        with open(desktop_file, 'r') as f:
                            for line in f:
                                if line.strip() == "Hidden=true":
                                    is_hidden = True
                                    break
                    except Exception as e:
                        self.logging.log(LogLevel.Warning, f"Could not read desktop file {desktop_file}: {e}")
                    
                    if is_hidden and hasattr(self, 'toggle2_switch') and not self.toggle2_switch.get_active():
                        continue
                    startup_apps[app_name] = {
                        "type": "desktop",
                        "path": desktop_file,
                        "name": app_name,
                        "enabled": True,
                        "hidden": is_hidden
                        }
                
                for desktop_file in glob.glob(str(autostart_dir / "*.desktop.disabled")):
                    app_name = os.path.basename(desktop_file).replace(".desktop.disabled", "")
                    startup_apps[app_name] = {
                        "type": "desktop",
                        "path": desktop_file,
                        "name": app_name,
                        "enabled": False,
                        "hidden": False
                        }
                    
        # Add hyprland and sway apps according to session
        if get_current_session() == "Hyprland":
            hypr_apps = get_hyprland_startup_apps()
            startup_apps.update(hypr_apps)
        if get_current_session() == "sway":
            sway_apps = get_sway_startup_apps()
            startup_apps.update(sway_apps)
    
        self.logging.log(LogLevel.Debug, f"Found {len(startup_apps)} autostart apps")
        return startup_apps
    
    def refresh_list(self):
        """Clear and repopulate the list of autostart apps"""
        # Run on a separate thread to avoid blocking the ui
        if hasattr(self, '_refresh_thread') and self._refresh_thread.is_alive():
            self.logging.log(LogLevel.Debug, "Refresh thread is already running")
        thread = threading.Thread(target=self.populate_list)
        thread.daemon = True
        thread.start()
    
    def populate_list(self):
        # Get apps first
        apps = self.get_startup_apps()
        self.startup_apps = apps
        
        # Clear list in main thread
        GLib.idle_add(self.clear_list)
        
        # Add each app in main thread
        for app_name, app in apps.items():
            GLib.idle_add(self.add_app_to_list, app_name, app)
    
    def clear_list(self):
        """Clear all items from the listbox"""
        children = self.listbox.get_children()
        for child in children:
            self.listbox.remove(child)
    
    def add_app_to_list(self, app_name, app):
        """Add a single app to the listbox"""
        self.logging.log(LogLevel.Debug, f"Adding app to list: {app_name}, enabled: {app['enabled']}")
        
        row = Gtk.ListBoxRow()
        row.get_style_context().add_class("app-row")
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.add(hbox)
        
        if app.get("hidden", False):
            hidden_icon = Gtk.Image.new_from_icon_name(
                "view-hidden-symbolic", Gtk.IconSize.SMALL_TOOLBAR
            )
            hidden_icon.set_tooltip_text("Hidden entry")
            hbox.pack_start(hidden_icon, False, False, 0)
            
        if not app.get("enabled", True):
            disabled_icon = Gtk.Image.new_from_icon_name(
                "gtk-stop-symbolic", Gtk.IconSize.SMALL_TOOLBAR
            )
            disabled_icon.set_tooltip_text("Disabled")
            hbox.pack_start(disabled_icon, False, False, 0)
        
        # app label
        label = Gtk.Label(label=app.get("name", app_name), xalign=0)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(Pango.WrapMode.WORD)
        label.set_max_width_chars(40)
        label.get_style_context().add_class("app-label")
        hbox.pack_start(label, True, True, 0)
        
        button_label = "Disable" if app["enabled"] else "Enable"
        button = Gtk.Button(label=button_label)
        button.get_style_context().add_class("toggle-button")
        button.get_style_context().add_class("enabled" if app["enabled"] else "disabled")
        button.connect("clicked", self.toggle_startup, app_name)
        hbox.pack_start(button, False, False, 0)
        
        row.app_name = app_name
        row.button = button
        self.listbox.add(row)
        row.show_all()

    def toggle_startup(self, button, app_name):
        app = self.startup_apps.get(app_name)
        
        if not app:
            self.logging.log(LogLevel.Warn, f"App not found : {app_name}")
            return
        
        self.logging.log(LogLevel.Info, f"Toggling app: {app_name}, current enabled: {app.get('enabled')}, type: {app.get('type')}")
        
        # for both .desktop and hyprland apps
        if app["type"] == "desktop" :
            new_path = app["path"] + ".disabled" if app["enabled"] else app["path"].replace(".disabled", "")
            try:
                os.rename(app["path"], new_path)
                app["path"] = new_path
                app["enabled"] = not app["enabled"]
                button.set_label("Disable" if app["enabled"] else "Enable")
            except OSError as error:
                self.logging.log(LogLevel.Error, f"Failed to toggle startup app: {error}")

        elif app["type"] == "hyprland":
            # hyprland specific case
            toggle_hyprland_startup(app_name)

            app["enabled"] = not app["enabled"]
            button.set_label("Disable" if app["enabled"] else "Enable")
            
            self.logging.log(LogLevel.Info, f"App toggled: {app_name}, enabled: {app['enabled']}")
        # for sway
        elif app["type"] == "sway":
            # sway specific case
            toggle_sway_startup(app_name)

            app["enabled"] = not app["enabled"]
            button.set_label("Disable" if app["enabled"] else "Enable")
            
            self.logging.log(LogLevel.Info, f"App toggled: {app_name}, enabled: {app['enabled']}")
        self.refresh_list()
            
            
    def on_scan_clicked(self, widget):
        self.logging.log(LogLevel.Info, "Manually refreshing autostart apps...")
        self.refresh_list()
        
    def check_external_changes(self):
        """Check for external changes and update the UI"""
        current_apps = self.get_startup_apps()

        # check if there's any difference between current and stored apps
        if self.has_changes(current_apps, self.startup_apps):
            self.logging.log(LogLevel.Info, "Detected external changes in autostart apps, updating UI")
            self.refresh_list()

        return True  
    
    def has_changes(self, new_apps, old_apps):
        """Check if there are differences between two app dictionaries"""
        if set(new_apps.keys()) != set(old_apps.keys()):
            return True
            
        for app_name, app_info in new_apps.items():
            if app_name not in old_apps:
                return True
            if app_info["enabled"] != old_apps[app_name]["enabled"]:
                return True
            if app_info["path"] != old_apps[app_name]["path"]:
                return True
                
        return False
