#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

from config.settings import load_settings, save_settings


class SettingsTab(Gtk.Box):
    """Tab for application settings"""
    
    __gsignals__ = {
        'tab-visibility-changed': (GObject.SignalFlags.RUN_LAST, None, (str, bool,)),
        'tab-order-changed': (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Set margins for dialog window context
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Create a scrolled window to ensure content is accessible
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.pack_start(scrolled_window, True, True, 0)
        
        # Create a container for the content
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.content_box.set_margin_top(10)
        self.content_box.set_margin_bottom(10)
        self.content_box.set_margin_start(10)
        self.content_box.set_margin_end(10)
        scrolled_window.add(self.content_box)

        # Load current settings
        self.settings = load_settings()
        
        # Create UI
        self.populate_settings()
        
        # Make sure everything is visible
        self.show_all()
        
        # Print a message confirming that the settings tab has been created
        print("Settings UI has been created and populated")

    def populate_settings(self):
        """Populate the settings tab with options"""
        # Remove existing children if any
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        # Header with Settings title and icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_bottom(20)

        settings_icon = Gtk.Image.new_from_icon_name(
            "preferences-system-symbolic", Gtk.IconSize.DIALOG
        )
        header_box.pack_start(settings_icon, False, False, 0)

        settings_label = Gtk.Label(label="Settings")
        settings_label.set_markup("<span size='x-large' weight='bold'>Settings</span>")
        header_box.pack_start(settings_label, False, False, 0)

        self.content_box.pack_start(header_box, False, False, 0)

        # Create a frame for the tab settings section
        settings_frame = Gtk.Frame()
        settings_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.content_box.pack_start(settings_frame, False, False, 10)
        
        # Tab settings section
        self.tab_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.tab_section.set_margin_top(10)
        self.tab_section.set_margin_bottom(10)
        self.tab_section.set_margin_start(10)
        self.tab_section.set_margin_end(10)
        settings_frame.add(self.tab_section)

        section_label = Gtk.Label(label="Tab Settings")
        section_label.set_markup("<span weight='bold'>Tab Settings</span>")
        section_label.set_halign(Gtk.Align.START)
        self.tab_section.pack_start(section_label, False, False, 0)

        # Create a switch for each tab
        tabs = ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display"]
        self.tab_switches = {}
        self.tab_rows = {}

        for tab_name in tabs:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            
            # Add up/down buttons
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            button_box.set_valign(Gtk.Align.CENTER)
            
            up_button = Gtk.Button()
            up_button.set_image(Gtk.Image.new_from_icon_name("go-up-symbolic", Gtk.IconSize.BUTTON))
            up_button.set_relief(Gtk.ReliefStyle.NONE)
            up_button.connect("clicked", self.on_move_up_clicked, tab_name)
            button_box.pack_start(up_button, False, False, 0)
            
            down_button = Gtk.Button()
            down_button.set_image(Gtk.Image.new_from_icon_name("go-down-symbolic", Gtk.IconSize.BUTTON))
            down_button.set_relief(Gtk.ReliefStyle.NONE)
            down_button.connect("clicked", self.on_move_down_clicked, tab_name)
            button_box.pack_start(down_button, False, False, 0)
            
            # Make buttons more compact
            up_button.set_size_request(24, 24)
            down_button.set_size_request(24, 24)
            
            row.pack_start(button_box, False, False, 0)
            
            # Add tab name and switch
            label = Gtk.Label(label=f"Show {tab_name} tab")
            label.set_halign(Gtk.Align.START)
            row.pack_start(label, True, True, 0)
            
            switch = Gtk.Switch()
            # Get visibility from settings or default to True
            visible = self.settings.get("visibility", {}).get(tab_name, True)
            switch.set_active(visible)
            switch.connect("notify::active", self.on_tab_visibility_changed, tab_name)
            # Set switch size
            switch.set_size_request(40, 20)
            switch.set_valign(Gtk.Align.CENTER)
            switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            switch_box.set_size_request(50, 24)
            switch_box.set_valign(Gtk.Align.CENTER)
            switch_box.pack_start(switch, True, False, 0)
            row.pack_end(switch_box, False, False, 0)
            
            self.tab_switches[tab_name] = switch
            self.tab_rows[tab_name] = row

        # Add rows in the correct order
        self.update_ui_order()

    def update_ui_order(self):
        """Update the order of rows in the UI to match the current tab order"""
        # Get current tab order
        tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display"])
        
        # Remove all rows from the section
        for row in self.tab_section.get_children():
            if isinstance(row, Gtk.Box) and row != self.tab_section.get_children()[0]:  # Skip the label
                self.tab_section.remove(row)
        
        # Add rows back in the correct order
        for tab_name in tab_order:
            if tab_name in self.tab_rows:
                self.tab_section.pack_start(self.tab_rows[tab_name], False, False, 5)

    def on_tab_visibility_changed(self, switch, gparam, tab_name):
        """Handle tab visibility changes"""
        active = switch.get_active()
        
        # Ensure visibility dict exists
        if "visibility" not in self.settings:
            self.settings["visibility"] = {}
            
        # Update settings
        self.settings["visibility"][tab_name] = active
        save_settings(self.settings)
        
        # Emit signal to notify the main window
        self.emit("tab-visibility-changed", tab_name, active)

    def on_move_up_clicked(self, button, tab_name):
        """Handle move up button click"""
        # Get current tab order
        tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display"])
        
        # Find current index
        current_index = tab_order.index(tab_name)
        if current_index > 0:
            # Swap with previous tab
            tab_order[current_index], tab_order[current_index - 1] = tab_order[current_index - 1], tab_order[current_index]
            
            # Update settings
            self.settings["tab_order"] = tab_order
            save_settings(self.settings)
            
            # Update UI order
            self.update_ui_order()
            
            # Emit signal to notify the main window
            self.emit("tab-order-changed", tab_order)

    def on_move_down_clicked(self, button, tab_name):
        """Handle move down button click"""
        # Get current tab order
        tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display"])
        
        # Find current index
        current_index = tab_order.index(tab_name)
        if current_index < len(tab_order) - 1:
            # Swap with next tab
            tab_order[current_index], tab_order[current_index + 1] = tab_order[current_index + 1], tab_order[current_index]
            
            # Update settings
            self.settings["tab_order"] = tab_order
            save_settings(self.settings)
            
            # Update UI order
            self.update_ui_order()
            
            # Emit signal to notify the main window
            self.emit("tab-order-changed", tab_order) 