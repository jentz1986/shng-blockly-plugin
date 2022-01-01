from lib.model.smartplugin import SmartPlugin
from lib.plugin import Plugins


class ShngPluginFunctionsToBlockly():

    def __init__(self):
        self.plugins = None
        self.plugin_functions_list = []

    def build_plugin_functions_list(self):
        # Duplicate of /modules/admin/api_plugins.py#L500-L519 rf. https://github.com/smarthomeNG/smarthome/blob/301e4968483079098b01f1e6853c9f358ca6f552/modules/admin/api_plugins.py#L500-L519
        if self.plugins == None:
            self.plugins = Plugins.get_instance()
        self.plugin_functions_list = []
        for x in self.plugins.return_plugins():
            if isinstance(x, SmartPlugin):
                plugin_config_name = x.get_configname()
                if x.metadata is not None:
                    api = x.metadata.get_plugin_function_defstrings(
                        with_type=True, with_default=True)
                    if api is not None:
                        for function in api:
                            self.plugin_functions_list.append(
                                plugin_config_name + "." + function)        
