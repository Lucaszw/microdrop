"""
Copyright 2011 Ryan Fobel

This file is part of Microdrop.

Microdrop is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Microdrop is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Microdrop.  If not, see <http://www.gnu.org/licenses/>.
"""

import gtk
import gobject
import os
import math
import time

import numpy as np

from protocol import Protocol, load as load_protocol
from utility import check_textentry, is_float, is_int
from plugin_manager import ExtensionPoint, IPlugin, SingletonPlugin, \
    implements, emit_signal


class ProtocolController(SingletonPlugin):
    implements(IPlugin)
    
    def __init__(self):
        self.name = "microdrop.gui.protocol_controller"
        self.app = None
        self.builder = None
        self.textentry_step_duration = None
        self.textentry_voltage = None
        self.textentry_frequency = None
        self.label_step_number = None
        self.textentry_voltage = None
        self.textentry_frequency = None
        self.label_step_number = None
        self.button_run_protocol = None
        self.textentry_protocol_repeats = None
        
    def on_app_init(self, app):
        self.app = app
        self.builder = app.builder
        
        self.textentry_step_duration = self.builder. \
            get_object("textentry_step_duration")
        self.textentry_voltage = self.builder.get_object("textentry_voltage")
        self.textentry_frequency = self.builder. \
            get_object("textentry_frequency")
        self.label_step_number = self.builder.get_object("label_step_number")
        self.textentry_voltage = self.builder.get_object("textentry_voltage")
        self.textentry_frequency = self.builder. \
            get_object("textentry_frequency")
        self.label_step_number = self.builder.get_object("label_step_number")
        self.textentry_protocol_repeats = self.builder.get_object(
            "self.textentry_protocol_repeats")        
        self.button_run_protocol = self.builder.get_object("button_run_protocol")
        
        app.signals["on_button_insert_step_clicked"] = self.on_insert_step
        app.signals["on_button_delete_step_clicked"] = self.on_delete_step
        app.signals["on_button_copy_step_clicked"] = self.on_copy_step
        app.signals["on_button_first_step_clicked"] = self.on_first_step
        app.signals["on_button_prev_step_clicked"] = self.on_prev_step
        app.signals["on_button_next_step_clicked"] = self.on_next_step
        app.signals["on_button_last_step_clicked"] = self.on_last_step
        app.signals["on_button_run_protocol_clicked"] = self.on_run_protocol
        app.signals["on_menu_new_protocol_activate"] = self.on_new_protocol
        app.signals["on_menu_load_protocol_activate"] = self.on_load_protocol
        app.signals["on_menu_rename_protocol_activate"] = self.on_rename_protocol
        app.signals["on_menu_save_protocol_activate"] = self.on_save_protocol
        app.signals["on_menu_save_protocol_as_activate"] = self.on_save_protocol_as
        app.signals["on_menu_add_frequency_sweep_activate"] = self.on_add_frequency_sweep
        app.signals["on_textentry_voltage_focus_out_event"] = \
                self.on_textentry_voltage_focus_out
        app.signals["on_textentry_voltage_key_press_event"] = \
                self.on_textentry_voltage_key_press
        app.signals["on_textentry_frequency_focus_out_event"] = \
                self.on_textentry_frequency_focus_out
        app.signals["on_textentry_frequency_key_press_event"] = \
                self.on_textentry_frequency_key_press
        app.signals["on_textentry_protocol_repeats_focus_out_event"] = \
                self.on_textentry_protocol_repeats_focus_out
        app.signals["on_textentry_protocol_repeats_key_press_event"] = \
                self.on_textentry_protocol_repeats_key_press
        app.signals["on_textentry_step_duration_focus_out_event"] = \
                self.on_textentry_step_duration_focus_out
        app.signals["on_textentry_step_duration_key_press_event"] = \
                self.on_textentry_step_duration_key_press
        app.protocol_controller = self

    def on_insert_step(self, widget, data=None):
        self.app.protocol.insert_step()
        self.app.main_window_controller.update()

    def on_copy_step(self, widget, data=None):
        self.app.protocol.copy_step()
        self.app.main_window_controller.update()

    def on_delete_step(self, widget, data=None):
        self.app.protocol.delete_step()
        self.app.main_window_controller.update()

    def on_first_step(self, widget=None, data=None):
        self.app.protocol.first_step()
        self.app.main_window_controller.update()

    def on_prev_step(self, widget=None, data=None):
        self.app.protocol.prev_step()
        self.app.main_window_controller.update()

    def on_next_step(self, widget=None, data=None):
        self.app.protocol.next_step()
        self.app.main_window_controller.update()

    def on_last_step(self, widget=None, data=None):
        self.app.protocol.last_step()
        self.app.main_window_controller.update()

    def on_new_protocol(self, widget, data=None):
        filename = None
        # delete all steps (this is necessary so that plugins will also
        # clear all steps
        while len(self.app.protocol.steps) > 1:
            self.app.protocol.delete_step()
        self.app.protocol.delete_step() # still need to delete the first step
        self.app.protocol = Protocol(self.app.dmf_device.max_channel()+1)
        self.app.main_window_controller.update()

    def on_load_protocol(self, widget, data=None):
        dialog = gtk.FileChooserDialog(title="Load protocol",
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL,
                                                gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_OPEN,
                                                gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(os.path.join("devices",
                                               self.app.dmf_device.name,
                                               "protocols"))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            try:
                emit_signal("on_protocol_changed", [load_protocol(filename)])
            except Exception, why:
                print why
                self.app.main_window_controller.error("Could not open %s" % filename)
        dialog.destroy()
        self.app.main_window_controller.update()

    def on_rename_protocol(self, widget, data=None):
        self.app.config_controller.save_protocol(rename=True)
    
    def on_save_protocol(self, widget, data=None):
        self.app.config_controller.save_protocol()
    
    def on_save_protocol_as(self, widget, data=None):
        self.app.config_controller.save_protocol(save_as=True)
    
    def on_add_frequency_sweep(self, widget, data=None):
        AddFrequencySweepDialog(self.app).run()
        self.app.main_window_controller.update()

    def on_textentry_step_duration_focus_out(self, widget, data=None):
        self.on_step_duration_changed()

    def on_textentry_step_duration_key_press(self, widget, event):
        if event.keyval == 65293: # user pressed enter
            self.on_step_duration_changed()

    def on_step_duration_changed(self):        
        self.app.protocol.current_step().duration = \
            check_textentry(self.textentry_step_duration,
                            self.app.protocol.current_step().duration,
                            int)

    def on_textentry_voltage_focus_out(self, widget, data=None):
        self.on_voltage_changed()

    def on_textentry_voltage_key_press(self, widget, event):
        if event.keyval == 65293: # user pressed enter
            self.on_voltage_changed()

    def on_voltage_changed(self):
        self.app.protocol.current_step().voltage = \
            check_textentry(self.textentry_voltage,
                            self.app.protocol.current_step().voltage,
                            float)
        self.update()
        
    def on_textentry_frequency_focus_out(self, widget, data=None):
        self.on_frequency_changed()

    def on_textentry_frequency_key_press(self, widget, event):
        if event.keyval == 65293: # user pressed enter
            self.on_frequency_changed()

    def on_frequency_changed(self):
        self.app.protocol.current_step().frequency = \
            check_textentry(self.textentry_frequency,
                            self.app.protocol.current_step().frequency/1e3,
                            float)*1e3
        self.update()

    def on_textentry_protocol_repeats_focus_out(self, widget, data=None):
        self.on_protocol_repeats_changed()
    
    def on_textentry_protocol_repeats_key_press(self, widget, event):
        if event.keyval == 65293: # user pressed enter
            self.on_protocol_repeats_changed()
    
    def on_protocol_repeats_changed(self):
        self.app.protocol.n_repeats = \
            check_textentry(self.textentry_protocol_repeats,
                            self.app.protocol.n_repeats,
                            int)
        self.update()
            
    def on_run_protocol(self, widget, data=None):
        if self.app.running:
            self.pause_protocol()
        else:
            self.run_protocol()

    def run_protocol(self):
        if self.app.control_board.connected() and\
            self.app.control_board.number_of_channels() < \
            self.app.protocol.n_channels:
            self.app.main_window_controller.warning("Warning: currently "
                "connected board does not have enough channels for this "
                "protocol.")
        self.app.running = True
        self.button_run_protocol.set_image(self.builder.get_object(
            "image_pause"))
        emit_signal("on_protocol_run")
        self.run_step()

    def pause_protocol(self):
        self.app.running = False
        self.button_run_protocol.set_image(self.builder.get_object(
            "image_play"))
        emit_signal("on_protocol_pause")
        self.app.experiment_log_controller.save()
        emit_signal("on_experiment_log_changed", self.app.experiment_log)        
        
    def run_step(self):
        self.app.main_window_controller.update()
        
        # run through protocol (even though device is not connected)
        if self.app.control_board.connected()==False:
            t = time.time()
            while time.time()-t < self.app.protocol.current_step().duration/1000.0:
                while gtk.events_pending():
                    gtk.main_iteration()

        if self.app.protocol.current_step_number < len(self.app.protocol)-1:
            self.app.protocol.next_step()
        elif self.app.protocol.current_repetition < self.app.protocol.n_repeats-1:
            self.app.protocol.next_repetition()
        else: # we're on the last step
            self.pause_protocol()

        if self.app.running:
            self.run_step()

    def update(self):
        self.textentry_step_duration.set_text(str(
            self.app.protocol.current_step().duration))
        self.textentry_voltage.set_text(str(
            self.app.protocol.current_step().voltage))
        self.textentry_frequency.set_text(str(
            self.app.protocol.current_step().frequency/1e3))
        self.label_step_number.set_text("Step: %d/%d\tRepetition: %d/%d" % 
            (self.app.protocol.current_step_number+1,
            len(self.app.protocol.steps),
            self.app.protocol.current_repetition+1,
            self.app.protocol.n_repeats))

        if self.app.control_board.connected() and \
            (self.app.realtime_mode or self.app.running):
            if self.app.func_gen.is_connected():
                self.app.func_gen.set_voltage(self.app.protocol.current_step().voltage*math.sqrt(2)/200)
                self.app.func_gen.set_frequency(self.app.protocol.current_step().frequency)
            else:
                self.app.control_board.set_waveform_voltage(float(self.app.protocol.current_step().voltage)*math.sqrt(2)/100)
                self.app.control_board.set_waveform_frequency(float(self.app.protocol.current_step().frequency))
            if self.app.realtime_mode:
                state = self.app.protocol.state_of_all_channels()
                max_channels = self.app.control_board.number_of_channels() 
                if len(state) >  max_channels:
                    if len(np.nonzero(state[max_channels:]>=1)[0]):
                        self.app.main_window_controller.warning("One or more "
                            "channels that are currently on are not available.")
                    state = state[0:max_channels]
                elif len(state) < max_channels:
                    state = np.concatenate([state, np.zeros(max_channels-len(state), int)])
                else:
                    assert(len(state)==max_channels)
                self.app.control_board.set_state_of_all_channels(state)

        
        data = {"step":self.app.protocol.current_step_number, 
                "time":time.time()}
        emit_signal("on_protocol_update", data)
        self.app.experiment_log.add_data(data)
                
    def on_dmf_device_changed(self, dmf_device):
        emit_signal("on_protocol_changed", [Protocol(dmf_device.max_channel()+1)])


class AddFrequencySweepDialog:
    def __init__(self, app):
        self.app = app
        builder = gtk.Builder()
        builder.add_from_file(os.path.join("gui",
                                           "glade",
                                           "frequency_sweep_dialog.glade"))
        self.dialog = builder.get_object("frequency_sweep_dialog")
        self.dialog.set_transient_for(app.main_window_controller.view)
        self.textentry_start_freq = \
            builder.get_object("textentry_start_freq")
        self.textentry_end_freq = \
            builder.get_object("textentry_end_freq")
        self.textentry_n_steps = \
            builder.get_object("textentry_n_steps")
        self.textentry_start_freq.set_text("0.1")
        self.textentry_end_freq.set_text("1e2")
        self.textentry_n_steps.set_text("30")
        
    def run(self):
        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            start_freq = self.textentry_start_freq.get_text() 
            end_freq = self.textentry_end_freq.get_text() 
            number_of_steps = self.textentry_n_steps.get_text()
            if is_float(start_freq) == False:
                self.app.main_window_controller.error("Invalid start frequency.")
            elif is_float(end_freq) == False:
                self.app.main_window_controller.error("Invalid end frequency.")
            elif is_int(number_of_steps) == False or number_of_steps < 1:
                self.app.main_window_controller.error("Invalid number of steps.")
            elif end_freq < start_freq:
                self.app.main_window_controller.error("End frequency must be greater than the start frequency.")
            else:
                frequencies = np.logspace(np.log10(float(start_freq)),
                                          np.log10(float(end_freq)),
                                          int(number_of_steps))
                for frequency in frequencies:
                    self.app.protocol.current_step().frequency = frequency*1e3
                    self.app.protocol.copy_step()
        self.dialog.hide()
        return response