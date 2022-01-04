#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
#                       René Frieß                  rene.friess@gmail.com
#                       Dirk Wallmeier                dirk@wallmeier.info
# Extended  2021-       Jens Höppner                
#########################################################################
#  Blockly plugin for SmartHomeNG
#
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################


from lib.model.smartplugin import SmartPlugin
from lib.logic import Logics          # für update der /etc/logic.yaml

from .webif import WebInterface
from .models.shng_blocks_factory import ShngBlockFactory
from .models.blockly_to_shng_logic import BlocklyToShngLogic


class Blockly(SmartPlugin):
    """
    Main class of the Plugin. Hosts the models to interact with and provides
    the update functions for the items
    """

    PLUGIN_VERSION = '1.8.2'

    def __init__(self, sh):
        # Call init code of parent class (SmartPlugin)
        super().__init__()

        # Model to prepare Dynamic XML from Items for Blockly
        self.blocks_factory = ShngBlockFactory()

        # Model to provide interface to SHNG-Logics files and API
        self.blockly_to_shng_logic = BlocklyToShngLogic(self.logger,
                                                        self.get_sh()._logic_dir,
                                                        self._parameters.get(
                                                            'section_prefix', '')
                                                        )
        
        if not self.init_webinterface(WebInterface):
            self.logger.error("Unable to start Webinterface")
            self._init_complete = False
        else:
            self.logger.debug("Init complete")

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.debug("Run method called")

        # Logics API is not available when initializing the Plugin, but after run it is.
        self.blockly_to_shng_logic.shng_logics_api = Logics.get_instance()
        
        self.alive = True

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.debug("Stop method called")
        self.alive = False

    def parse_item(self, item):
        """
        Plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference
        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.
        """
        pass

    def parse_logic(self, logic):
        """
        Plugin parse_logic method
        """
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Write items values
        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        if self.alive and caller != self.get_shortname():
            # code to execute if the plugin is not stopped
            # and only, if the item has not been changed by this this plugin:
            self.logger.info(
                f"Update item: {item.property.path}, item has been changed outside this plugin")
