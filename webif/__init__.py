#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
#                       René Frieß                  rene.friess@gmail.com
#                       Dirk Wallmeier                dirk@wallmeier.info
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.5 and
#  upwards.
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

import time
import json
import cherrypy
from cherrypy.lib.static import serve_file

from lib.model.smartplugin import SmartPluginWebIf


class WebInterface(SmartPluginWebIf):

    logics = None

    cmd = ''

    def __init__(self, webif_dir, plugin):
        """
        Initialization of instance of class WebInterface

        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.logger = plugin.logger
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.blocks_factory = self.plugin.blocks_factory

        self.logger.info('Blockly Webif.__init__')

        self.tplenv = self.init_template_environment()

    @cherrypy.expose
    def index(self, reload=None):
        cherrypy.lib.caching.expires(0)

        tmpl = self.tplenv.get_template('blockly.html')
        return tmpl.render(cmd=self.cmd,
                           p=self.plugin,
                           timestamp=str(time.time()))

    @cherrypy.expose
    def blockly_load_logic(self, uniq_param, logic_name):
        """
        the uniq-param is used to unify the request from jquery-side, 
        if the parameter is deleted here, the call will fail
        """
        try:
            fn_xml = self.plugin.blockly_to_shng_logic.get_blockly_logic_file_name(
                logic_name)
            return serve_file(fn_xml, content_type='application/xml')
        except FileNotFoundError:
            cherrypy.response.status = 404
            return f"Logic {logic_name} not found"

    @cherrypy.expose
    def blockly_save_logic(self, py, xml, name):
        """ Save the logic - Saves the Blocky xml and the Python code """
        self.plugin.blockly_to_shng_logic.save_logic(logic_name=name,
                                                     python_code=py,
                                                     blockly_xml=xml)

    @cherrypy.expose
    def blockly_get_logics(self, uniq_param):
        cherrypy.response.headers['Content-Type'] = 'text/json'
        return json.dumps(self.plugin.blockly_to_shng_logic.get_blockly_logics())

    @cherrypy.expose
    def toolbox_xml(self):
        cherrypy.response.headers['Content-Type'] = 'text/xml'
        return self.blocks_factory.get_toolbox_xml_string()

    @cherrypy.expose
    def toolbox_json(self, pretty=False):
        cherrypy.response.headers['Content-Type'] = 'text/json'
        if pretty:
            return json.dumps(self.blocks_factory.get_toolbox_dict_for_json(), indent=4)
        return json.dumps(self.blocks_factory.get_toolbox_dict_for_json())
