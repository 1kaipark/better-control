# Copyright (C) 2025 [quantumvoid0](https://github.com/quantumvoid0)
# This program is licensed under the terms of the GNU General Public License v3.
# See LICENSE.md for the full license text.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

import gi
import os
import shutil
import time
from pydbus import SystemBus
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib, Gdk  
import subprocess

class HyprlandSettingsApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Control Center")
        self.set_default_size(900, 700)

        notebook = Gtk.Notebook()
        self.add(notebook)

        wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        wifi_box.set_margin_top(10)
        wifi_box.set_margin_bottom(10)
        wifi_box.set_margin_start(10)
        wifi_box.set_margin_end(10)

        self.wifi_listbox = Gtk.ListBox()
        self.wifi_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        wifi_box.pack_start(self.wifi_listbox, True, True, 0)

        wifi_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        refresh_wifi_button = Gtk.Button(label="Refresh")
        refresh_wifi_button.connect("clicked", self.refresh_wifi)
        wifi_button_box.pack_start(refresh_wifi_button, False, False, 0)

        connect_wifi_button = Gtk.Button(label="Connect")
        connect_wifi_button.connect("clicked", self.connect_wifi)
        wifi_button_box.pack_start(connect_wifi_button, False, False, 0)

        forget_wifi_button = Gtk.Button(label="Forget")
        forget_wifi_button.connect("clicked", self.forget_wifi)
        wifi_button_box.pack_start(forget_wifi_button, False, False, 0)

        disconnect_wifi_button = Gtk.Button(label="Disconnect")
        disconnect_wifi_button.connect("clicked", self.disconnect_wifi)
        wifi_button_box.pack_start(disconnect_wifi_button, False, False, 0)

        wifi_box.pack_start(wifi_button_box, False, False, 0)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)  
        self.password_entry.set_placeholder_text("Enter Wi-Fi password")
        wifi_box.pack_start(self.password_entry, False, False, 0)

        notebook.append_page(wifi_box, Gtk.Label(label="Wi-Fi"))

        bluetooth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        bluetooth_box.set_margin_top(10)
        bluetooth_box.set_margin_bottom(10)
        bluetooth_box.set_margin_start(10)
        bluetooth_box.set_margin_end(10)

        self.bt_listbox = Gtk.ListBox()
        self.bt_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        bluetooth_box.pack_start(self.bt_listbox, True, True, 0)

        bluetooth_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        enable_bt_button = Gtk.Button(label="Enable Bluetooth")
        enable_bt_button.connect("clicked", self.enable_bluetooth)
        bluetooth_button_box.pack_start(enable_bt_button, False, False, 0)

        disable_bt_button = Gtk.Button(label="Disable Bluetooth")
        disable_bt_button.connect("clicked", self.disable_bluetooth)
        bluetooth_button_box.pack_start(disable_bt_button, False, False, 0)

        refresh_bt_button = Gtk.Button(label="Refresh Devices")
        refresh_bt_button.connect("clicked", self.refresh_bluetooth)
        bluetooth_button_box.pack_start(refresh_bt_button, False, False, 0)

        bluetooth_box.pack_start(bluetooth_button_box, False, False, 0)

        notebook.append_page(bluetooth_box, Gtk.Label(label="Bluetooth"))

        volume_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        volume_box.set_margin_top(10)
        volume_box.set_margin_bottom(10)
        volume_box.set_margin_start(10)
        volume_box.set_margin_end(10)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(False)
        volume_box.pack_start(grid, False, False, 0)
        grid.set_column_spacing(10)

        mainlabel = Gtk.Label(label="Quick Controls")
        volume_label = Gtk.Label(label="Speaker Volume")
        mic_label = Gtk.Label(label="Microphone Volume")  
        volume_label.set_xalign(0)
        mic_label.set_xalign(0)
        mainlabel.set_xalign(0)

        sep1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        self.volume_button = Gtk.Button(label=f"Mute/Unmute Speaker")
        self.volume_button.connect("clicked", self.mute)
        self.volume_button.set_hexpand(True)

        self.volume_mic = Gtk.Button(label=f"Mute/Unmute Mic")
        self.volume_mic.connect("clicked", self.micmute)
        self.volume_mic.set_hexpand(True)

        self.volume_zero = Gtk.Button(label="0%")  
        self.volume_zero.set_size_request(200, -1)  
        self.volume_zero.connect("clicked",self.vzero)
        self.volume_zero.set_hexpand(True)  

        self.volume_tfive = Gtk.Button(label="25%")  
        self.volume_tfive.set_size_request(200, -1)  
        self.volume_tfive.connect("clicked",self.vtfive)
        self.volume_tfive.set_hexpand(True)  

        self.volume_fifty = Gtk.Button(label="50%")  
        self.volume_fifty.set_size_request(200, -1)  
        self.volume_fifty.connect("clicked",self.vfifty)
        self.volume_fifty.set_hexpand(True)  

        self.volume_sfive = Gtk.Button(label="75%")  
        self.volume_sfive.set_size_request(200, -1)  
        self.volume_sfive.connect("clicked",self.vsfive)
        self.volume_sfive.set_hexpand(True)  

        self.volume_hund = Gtk.Button(label="100%")  
        self.volume_hund.set_size_request(200, -1)  
        self.volume_hund.connect("clicked",self.vhund)
        self.volume_hund.set_hexpand(True) 

        self.mic_zero = Gtk.Button(label="0%")  
        self.mic_zero.set_size_request(200, -1)  
        self.mic_zero.connect("clicked",self.mzero)
        self.mic_zero.set_hexpand(True)  

        self.mic_tfive = Gtk.Button(label="25%")  
        self.mic_tfive.set_size_request(200, -1)  
        self.mic_tfive.connect("clicked",self.mtfive)
        self.mic_tfive.set_hexpand(True)  

        self.mic_fifty = Gtk.Button(label="50%")  
        self.mic_fifty.set_size_request(200, -1)  
        self.mic_fifty.connect("clicked",self.mfifty)
        self.mic_fifty.set_hexpand(True)  

        self.mic_sfive = Gtk.Button(label="75%")  
        self.mic_sfive.set_size_request(200, -1)  
        self.mic_sfive.connect("clicked",self.msfive)
        self.mic_sfive.set_hexpand(True)  

        self.mic_hund = Gtk.Button(label="100%")  
        self.mic_hund.set_size_request(200, -1)  
        self.mic_hund.connect("clicked",self.mhund)
        self.mic_hund.set_hexpand(True)  

        self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume_scale.set_hexpand(True)  
        self.volume_scale.set_value(self.get_current_volume())
        self.volume_scale.set_value_pos(Gtk.PositionType.BOTTOM)  
        self.volume_scale.connect("value-changed", self.set_volume)

        self.mic_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.mic_scale.set_hexpand(True)  
        self.mic_scale.set_value_pos(Gtk.PositionType.BOTTOM)  
        self.mic_scale.set_value(self.get_current_mic_volume())
        self.mic_scale.connect("value-changed", self.set_mic_volume)
        self.mic_scale.set_value_pos(Gtk.PositionType.LEFT)

        grid.attach(self.volume_zero, 0, 2, 1, 1)
        grid.attach(self.volume_tfive, 1, 2, 1, 1)        
        grid.attach(self.volume_fifty, 2, 2, 1, 1)
        grid.attach(self.volume_sfive, 3, 2, 1, 1)
        grid.attach(self.volume_hund, 4, 2, 1, 1)

        grid.attach(self.mic_zero, 0, 6, 1, 1)
        grid.attach(self.mic_tfive, 1, 6, 1, 1)        
        grid.attach(self.mic_fifty, 2, 6, 1, 1)
        grid.attach(self.mic_sfive, 3, 6, 1, 1)
        grid.attach(self.mic_hund, 4, 6, 1, 1)

        grid.set_row_spacing(15)  

        self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume_scale.set_draw_value(True)
        self.volume_scale.set_value_pos(Gtk.PositionType.LEFT)
        self.volume_scale.set_hexpand(True)

        grid.attach(self.volume_mic, 0, 10, 1, 1)
        grid.attach(self.volume_button, 1, 10, 1, 1)
        grid.attach(volume_label, 0, 1, 5, 1)  
        grid.attach(mic_label, 0, 5, 5, 1)  
        grid.attach(self.volume_scale, 0, 3, 5, 1) 
        grid.attach(self.mic_scale,0,7,5,1)
        grid.attach(sep1,0,4,5,1)
        grid.attach(sep2,0,8,5,1)
        grid.attach(mainlabel,0,9,5,1)

        self.volume_scale.set_value(self.get_current_volume())
        self.volume_scale.connect("value-changed", self.set_volume)

        volume_box.pack_start(grid, False, False, 0)

        notebook.append_page(volume_box, Gtk.Label(label="Volume"))

        brightness_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        brightness_box.set_margin_top(10)
        brightness_box.set_margin_bottom(10)
        brightness_box.set_margin_start(10)
        brightness_box.set_margin_end(10)        

        grid = Gtk.Grid()
        grid.set_column_homogeneous(False)  
        brightness_box.pack_start(grid, False, False, 0)
        grid.set_column_spacing(10)

        self.brightness_zero = Gtk.Button(label="0%")  
        self.brightness_zero.set_size_request(200, -1)  
        self.brightness_zero.connect("clicked",self.zero)
        self.brightness_zero.set_hexpand(True)  

        self.brightness_tfive = Gtk.Button(label="25%")  
        self.brightness_tfive.set_size_request(200, -1)  
        self.brightness_tfive.connect("clicked",self.tfive)
        self.brightness_tfive.set_hexpand(True)  

        self.brightness_fifty = Gtk.Button(label="50%")  
        self.brightness_fifty.set_size_request(200, -1)  
        self.brightness_fifty.connect("clicked",self.fifty)
        self.brightness_fifty.set_hexpand(True)  

        self.brightness_sfive = Gtk.Button(label="75%")  
        self.brightness_sfive.set_size_request(200, -1)  
        self.brightness_sfive.connect("clicked",self.sfive)
        self.brightness_sfive.set_hexpand(True)  

        self.brightness_hund = Gtk.Button(label="100%")  
        self.brightness_hund.set_size_request(200, -1)  
        self.brightness_hund.connect("clicked",self.hund)
        self.brightness_hund.set_hexpand(True)  

        self.brightness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.brightness_scale.set_hexpand(True)  
        self.brightness_scale.set_value(self.get_current_brightness())
        self.brightness_scale.set_value_pos(Gtk.PositionType.BOTTOM)  
        self.brightness_scale.connect("value-changed", self.set_brightness)

        grid.attach(self.brightness_zero, 0, 0, 1, 1)
        grid.attach(self.brightness_tfive, 1, 0, 1, 1)        
        grid.attach(self.brightness_fifty, 2, 0, 1, 1)
        grid.attach(self.brightness_sfive, 3, 0, 1, 1)
        grid.attach(self.brightness_hund, 4, 0, 1, 1)
        grid.attach(self.brightness_scale, 0, 2, 5, 1)  

        notebook.append_page(brightness_box, Gtk.Label(label="Brightness"))

        self.update_button_labels()

    def enable_bluetooth(self, button):
        if not shutil.which("bluetoothctl"):
            self.show_error("BlueZ is not installed. Install it with:\n\nsudo pacman -S bluez bluez-utils")
            return  

        print("Enabling Bluetooth...")
        subprocess.run(["systemctl", "start", "bluetooth"])

        for _ in range(5):
            bt_status = subprocess.run(["systemctl", "is-active", "bluetooth"], capture_output=True, text=True).stdout.strip()
            if bt_status == "active":
                print("Bluetooth enabled.")
                return
            subprocess.run(["sleep", "1"])  

        self.show_error("Failed to enable Bluetooth. Make sure BlueZ is installed.")

    def disable_bluetooth(self, button):
        print("Disabling Bluetooth...")
        subprocess.run(["systemctl", "stop", "bluetooth"])
        print("Bluetooth disabled.")

    def refresh_bluetooth(self, button):
        """ Refreshes the list of Bluetooth devices (paired + nearby) """
        self.bt_listbox.foreach(lambda row: self.bt_listbox.remove(row))

        bt_status = subprocess.run(
            ["systemctl", "is-active", "bluetooth"], capture_output=True, text=True
        ).stdout.strip()
        if bt_status != "active":
            self.show_error("Bluetooth is disabled. Enable it first.")
            return

        subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, text=True)
        time.sleep(5)  
        subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, text=True)

        output = subprocess.run(
            ["bluetoothctl", "devices"], capture_output=True, text=True
        ).stdout.strip()
        devices = output.split("\n")

        if not devices or devices == [""]:
            self.show_error("No Bluetooth devices found nearby.")
            return

        for device in devices:
            parts = device.split(" ")
            if len(parts) < 2:
                continue
            mac_address = parts[1]
            device_name = " ".join(parts[2:]) if len(parts) > 2 else mac_address

            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            label = Gtk.Label(label=device_name, xalign=0)
            connect_button = Gtk.Button(label="Connect")
            disconnect_button = Gtk.Button(label="Disconnect")

            connect_button.connect("clicked", self.connect_bluetooth_device, mac_address)
            disconnect_button.connect("clicked", self.disconnect_bluetooth_device, mac_address)

            box.pack_start(label, True, True, 0)
            box.pack_start(connect_button, False, False, 0)
            box.pack_start(disconnect_button, False, False, 0)

            row.add(box)

            self.bt_listbox.add(row)

        self.bt_listbox.show_all()

    def show_error(self, message):
        """ Displays an error message in a popup """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

    def connect_bluetooth_device(self, button, mac_address):
        """ Connects to a selected Bluetooth device """
        try:
            subprocess.run(["bluetoothctl", "pair", mac_address], capture_output=True, text=True)
            subprocess.run(["bluetoothctl", "connect", mac_address], capture_output=True, text=True)
        except Exception as e:
            self.show_error(f"Error connecting to {mac_address}: {e}")

    def disconnect_bluetooth_device(self, button, mac_address):
        """ Disconnects from a selected Bluetooth device """
        try:
            subprocess.run(["bluetoothctl", "disconnect", mac_address], capture_output=True, text=True)
        except Exception as e:
            self.show_error(f"Error disconnecting from {mac_address}: {e}")

    def forget_bluetooth_device(self, button, mac_address):
        """ Removes a Bluetooth device from known devices """
        try:
            subprocess.run(["bluetoothctl", "remove", mac_address], capture_output=True, text=True)
        except Exception as e:
            self.show_error(f"Error forgetting {mac_address}: {e}")

    def mzero(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "0%"])
        self.mic_scale.set_value(0)

    def mtfive(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "25%"])
        self.mic_scale.set_value(25)

    def mfifty(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "50%"])
        self.mic_scale.set_value(50)

    def msfive(self,button):
       subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "75%"])    
       self.mic_scale.set_value(75)

    def mhund(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "100%"])
        self.mic_scale.set_value(100)

    def vzero(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "0%"])
        self.volume_scale.set_value(0)

    def vtfive(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "25%"])
        self.volume_scale.set_value(25)

    def vfifty(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "50%"])
        self.volume_scale.set_value(50)

    def vsfive(self,button):
       subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "75%"])    
       self.volume_scale.set_value(75)

    def vhund(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "100%"])
        self.volume_scale.set_value(100)

    def zero(self,button):
        subprocess.run(['brightnessctl', 's', '0'])
        self.brightness_scale.set_value(0)

    def tfive(self,button):
        subprocess.run(['brightnessctl', 's', '25'])
        self.brightness_scale.set_value(25)

    def fifty(self,button):
        subprocess.run(['brightnessctl', 's', '50'])
        self.brightness_scale.set_value(50)

    def sfive(self,button):
        subprocess.run(['brightnessctl', 's', '75'])
        self.brightness_scale.set_value(75)

    def hund(self,button):
        subprocess.run(['brightnessctl', 's', '100'])
        self.brightness_scale.set_value(100)

    def set_mic_volume(self, scale):
        new_volume = int(scale.get_value())
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{new_volume}%"])

    def get_current_mic_volume(self):
        try:
            output = subprocess.run(["pactl", "get-source-volume", "@DEFAULT_SOURCE@"], capture_output=True, text=True).stdout
            return int(output.split()[4].replace("%", ""))
        except Exception as e:
            print("Error getting mic volume:", e)
            return 50  

    def refresh_wifi(self, button):
        self.wifi_listbox.foreach(lambda row: self.wifi_listbox.remove(row))
        networks = subprocess.getoutput("nmcli dev wifi").split("\n")[1:]
        for network in networks:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=network)
            row.add(label)
            self.wifi_listbox.add(row)
        self.wifi_listbox.show_all()

    def connect_wifi(self, button):
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            print("No Wi-Fi network selected.")
            return

        ssid = selected_row.get_child().get_text().split()[1]
        print(f"Selected SSID: {ssid}")

        if "secured" in selected_row.get_child().get_text().lower():
            print("Network is secured. Using password from input field...")
            password = self.password_entry.get_text()
            if not password:
                print("No password entered.")
                return

            try:
                result = subprocess.run(
                    ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"Successfully connected: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to connect: {e.stderr}")
        else:
            print("Network is unsecured. Attempting to connect...")
            try:
                result = subprocess.run(
                    ["nmcli", "dev", "wifi", "connect", ssid],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"Successfully connected: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to connect: {e.stderr}")

    def forget_wifi(self, button):
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            return
        ssid = selected_row.get_child().get_text().split()[1]
        try:
            connections = subprocess.getoutput(f"nmcli -t -f NAME,UUID connection show | grep '{ssid}'").split("\n")
            if not connections or not connections[0]:  
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"No saved connection found for '{ssid}'."
                )
                dialog.run()
                dialog.destroy()
                return
            uuid = connections[0].split(":")[1]
            subprocess.run(["nmcli", "connection", "delete", "uuid", uuid], check=True)
            self.refresh_wifi(None)  
        except subprocess.CalledProcessError as e:
            print(f"Failed to forget network: {e}")

    def disconnect_wifi(self, button):
        try:
            subprocess.run(["nmcli", "dev", "disconnect", "wlo1"], check=True)  
        except subprocess.CalledProcessError as e:
            print(f"Failed to disconnect: {e}")

    def get_current_volume(self):
        output = subprocess.getoutput("pactl get-sink-volume @DEFAULT_SINK@")
        volume = int(output.split("/")[1].strip().strip("%"))
        return volume

    def set_volume(self, scale):
        value = int(scale.get_value())
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"])

    def get_current_brightness(self):
        output = subprocess.getoutput("brightnessctl get")
        max_brightness = subprocess.getoutput("brightnessctl max")
        return int((int(output) / int(max_brightness)) * 100)

    def set_brightness(self, scale):
        value = int(scale.get_value())
        subprocess.run(["brightnessctl", "set", f"{value}%"])

    def is_muted(self, audio_type="sink"):
        """
        Check if the audio sink or source is currently muted.
        :param audio_type: "sink" for speaker, "source" for microphone
        :return: True if muted, False otherwise
        """
        try:
            if audio_type == "sink":
                output = subprocess.getoutput("pactl get-sink-mute @DEFAULT_SINK@")
            elif audio_type == "source":
                output = subprocess.getoutput("pactl get-source-mute @DEFAULT_SOURCE@")
            else:
                raise ValueError("Invalid audio_type. Use 'sink' or 'source'.")

            return "yes" in output.lower()
        except Exception as e:
            print(f"Error checking mute state: {e}")
            return False

    def update_button_labels(self):
        """
        Update the labels of the mute/unmute buttons based on the current mute state.
        """
        try:

            if self.is_muted("sink"):
                self.volume_button.set_label("Unmute Speaker")
            else:
                self.volume_button.set_label("Mute Speaker")

            if self.is_muted("source"):
                self.volume_mic.set_label("Unmute Mic")
            else:
                self.volume_mic.set_label("Mute Mic")
        except Exception as e:
            print(f"Error updating button labels: {e}")

    def mute(self, button):
        """
        Toggle mute/unmute for the speaker dynamically and update the button label.
        """
        try:
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
            print("Speaker mute state toggled.")

            self.update_button_labels()
        except Exception as e:
            print(f"Error toggling speaker mute state: {e}")

    def micmute(self, button):
        """
        Toggle mute/unmute for the microphone dynamically and update the button label.
        """
        try:
            subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])
            print("Microphone mute state toggled.")

            self.update_button_labels()
        except Exception as e:
            print(f"Error toggling microphone mute state: {e}")

if __name__ == "__main__":
    win = HyprlandSettingsApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


