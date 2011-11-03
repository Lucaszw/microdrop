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

import os
import time

import gtk

from experiment_log import ExperimentLog, load as load_experiment_log
from utility import path, combobox_set_model_from_list, \
    combobox_get_active_text, textview_get_text
from plugin_manager import IPlugin, SingletonPlugin, implements, \
    ExtensionPoint, emit_signal
from protocol import load as load_protocol
from dmf_device import load as load_dmf_device

class ExperimentLogController(SingletonPlugin):
    implements(IPlugin)

    def __init__(self):
        self.name = "microdrop.gui.experiment_log_controller" 
        self.app = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join("gui","glade",
            "experiment_log_window.glade"))
        self.window = self.builder.get_object("window")
        self.combobox_log_files = self.builder.get_object("combobox_log_files")
        self.results_log = None

    def on_app_init(self, app):
        self.app = app
        self.app.experiment_log_controller = self
        self.window.set_title("Experiment logs")
        self.builder.connect_signals(self)

    def update(self):
        try:
            id = combobox_get_active_text(self.combobox_log_files)
            f = path(self.app.experiment_log.directory) / path(id) / path("data")
            self.results_log = load_experiment_log(f)

            self.builder.get_object("button_load_device").set_sensitive(True)        
            self.builder.get_object("button_load_protocol").set_sensitive(True)    
            self.builder.get_object("textview_notes").set_sensitive(True)
            
            label = "Software version: "
            val = self.results_log.get("software version")
            if len(val) and val[0]:
                label += val[0]
            self.builder.get_object("label_software_version"). \
                set_text(label)

            label = "Device: "
            val = self.results_log.get("device name")
            if len(val) and val[0]:
                label += val[0]
            self.builder.get_object("label_device"). \
                set_text(label)

            label = "Protocol: "
            val = self.results_log.get("protocol name")
            if len(val) and val[0]:
                label += val[0]
            else:
                label += "None"
            self.builder.get_object("label_protocol"). \
                set_text(label)
            
            label = "Control board: "
            val = self.results_log.get("control board name")
            if len(val) and val[0]:
                label += val[0]
                val = self.results_log.get("control board hardware version")
                if len(val) and val[0]:
                    label += " v%s" % val[0]
                val = self.results_log.get("control board software version")
                if len(val) and val[0]:
                    label += "\n\tFirmware version:%s" % val[0]
            else:
                label += "None"
            self.builder.get_object("label_control_board"). \
                set_text(label)
            
            label = "Time of experiment: "
            val = self.results_log.get("experiment time")
            if len(val) and val[0]:
                label += time.ctime(val[0])
            self.builder.get_object("label_experiment_time"). \
                set_text(label)
            
            val = self.results_log.get("notes")
            if len(val) and val[0]:
                label = val[0]
            else:
                label = ""
            self.builder.get_object("textview_notes"). \
                get_buffer().set_text(label)
        except:
            self.builder.get_object("button_load_device").set_sensitive(False)        
            self.builder.get_object("button_load_protocol").set_sensitive(False)    
            self.builder.get_object("textview_notes").set_sensitive(False)
    
    def save(self):
        data = {"software version":self.app.version}
        data["device name"] = self.app.dmf_device.name
        data["protocol name"] = self.app.protocol.name
        data["experiment time"] = time.time()
        if self.app.control_board.connected():
            data["control board name"] = \
                self.app.control_board.name()
            data["control board hardware version"] = \
                self.app.control_board.hardware_version()
            data["control board software version"] = \
                self.app.control_board.software_version()
        data["notes"] = textview_get_text(self.app.protocol_controller. \
            builder.get_object("textview_notes"))
        self.app.experiment_log.add_data(0, data)
        log_path = self.app.experiment_log.save()

        # save the protocol and device
        self.app.protocol.save(os.path.join(log_path,"protocol"))
        self.app.dmf_device.save(os.path.join(log_path,"device"))
        self.app.experiment_log.clear()
        emit_signal("on_experiment_log_changed", self.app.experiment_log)
        self.app.main_window_controller.update()

    def on_window_show(self, widget, data=None):
        self.window.show()
        
    def on_window_delete_event(self, widget, data=None):
        self.window.hide()
        return True
        
    def on_combobox_log_files_changed(self, widget, data=None):
        self.update()
    
    def on_button_load_device_clicked(self, widget, data=None):
        filename = path(os.path.join(self.app.experiment_log.directory,
                                     str(self.results_log.experiment_id),
                                     'device')) 
        try:
            emit_signal("on_dmf_device_changed", [load_dmf_device(filename)])
        except:
            self.app.main_window_controller.error("Could not open %s" % filename)
        self.app.main_window_controller.update()
        
    def on_button_load_protocol_clicked(self, widget, data=None):
        filename = path(os.path.join(self.app.experiment_log.directory,
                                     str(self.results_log.experiment_id),
                                     'protocol'))
        try:
            emit_signal("on_protocol_changed", [load_protocol(filename)])
        except:
            self.app.main_window_controller.error("Could not open %s" % filename)
        self.app.main_window_controller.update()

    def on_textview_notes_focus_out_event(self, widget, data=None):
        if len(self.results_log.data[0])==0:
            self.results_log.data.append({})
        self.results_log.data[0]["notes"] = textview_get_text(self.builder. \
            get_object("textview_notes"))
        filename = os.path.join(self.results_log.directory,
                                str(self.results_log.experiment_id),
                                'data')
        self.results_log.save(filename)

    def on_dmf_device_changed(self, dmf_device):
        device_path = None
        if dmf_device.name:
            device_path = os.path.join(self.app.config.dmf_device_directory,
                                       dmf_device.name, "logs")
        experiment_log = ExperimentLog(device_path)
        emit_signal("on_experiment_log_changed", [experiment_log])
        
    def on_experiment_log_changed(self, dmf_device):
        log_files = []
        for d in path(self.app.experiment_log.directory).dirs():
            f = d / path("data")
            if f.isfile():
                log_files.append(int(d.name))
        log_files.sort()
        self.combobox_log_files.clear()
        combobox_set_model_from_list(self.combobox_log_files, log_files)
        if len(log_files):
            self.combobox_log_files.set_active(len(log_files)-1)
        self.update()