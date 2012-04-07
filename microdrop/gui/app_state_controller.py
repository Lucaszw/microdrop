import logging

from plugin_manager import SingletonPlugin, implements, \
    IPlugin, IAppStatePlugin, PluginGlobals, ScheduleRequest, emit_signal
from app_state import AppState
from app_context import get_app


PluginGlobals.push_env('microdrop')


class AppStateController(SingletonPlugin):
    implements(IPlugin)
    implements(IAppStatePlugin)

    name = 'microdrop.gui.app_state_controller'

    def __init__(self):
        pass

    def on_plugin_enable(self, *args, **kwargs):
        print '[AppStateController] on_plugin_enable()'
        app = get_app()
        app.app_state_controller = self
        self.app_state = app.state
        self.app_state.on_pre_event = self._on_pre_event
        self.app_state.on_post_event = self._on_post_event

    def on_app_init(self, *args, **kwargs):
        self.on_plugin_enable(*args, **kwargs)

    def on_pre_event(self, state, event):
        logging.debug('[on_pre_event] state=%s, event=%s' % (state,
                event.type.split(' ')[-1]))

    def on_post_event(self, state, event):
        logging.debug('[on_post_event] state=%s, event=%s' % (state,
                event.type.split(' ')[-1]))

    def _on_pre_event(self, state, event):
        emit_signal('on_pre_event', [state, event], interface=IAppStatePlugin)

    def _on_post_event(self, state, event):
        emit_signal('on_post_event', [state, event], interface=IAppStatePlugin)

    def get_schedule_requests(self, function_name):
        """
        Returns a list of scheduling requests (i.e., ScheduleRequest
        instances) for the function specified by function_name.
        """
        if function_name in ['on_app_init', 'on_plugin_enable']:
            app = get_app()
            schedule_requests = []
            for p in [name for name in app.core_plugins if name != self.name]:
                schedule_request = ScheduleRequest(self.name, p)
                schedule_requests.append(schedule_request)
            return schedule_requests
        return []
    

PluginGlobals.pop_env()