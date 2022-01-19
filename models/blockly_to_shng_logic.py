import re
from os import path, walk
from lib.utils import Utils


class BlocklyToShngLogic():

    def __init__(self, logger, logics_directory_name, section_prefix):
        self.logger = logger
        self.logics_directory_name = logics_directory_name
        self.logics_template_dir_name = path.join(
            path.join(path.dirname(__file__), '..'), 'logic_templates')
        self.logic_yaml_section_prefix = section_prefix

        self.logger.debug(f"Logics Directory: '{self.logics_directory_name}'")
        self.logger.debug(
            f"Template Directory: '{self.logics_template_dir_name}'")

    def __pretty_print_xml(self, xml_in):
        import xml.dom.minidom

        xml = xml.dom.minidom.parseString(xml_in)
        xml_out = xml.toprettyxml()
        return xml_out

    def __sanitize_file_name(self, raw_name):
        sanitized_name = re.sub("[^0-9a-zA-Z-\_]+", "_", raw_name)
        sanitized_name = sanitized_name.replace('___', '_').replace('__', '_')
        return sanitized_name.lower()

    def get_blockly_logics(self):
        self.logger.debug('get_blockly_logics called')
        logic_names = []
        filenames = next(walk(self.logics_directory_name),
                         (None, None, []))[2]  # [] if no file
        for filename in filenames:
            if filename.endswith('.blockly'):
                logic_names.append(filename[:-8])
        return logic_names

    def get_blockly_logic_file_name(self, logic_name=None):
        self.logger.debug(
            f"get_blockly_logic_file_name: logic_name = '{logic_name}'")
        original_logic_name = logic_name
        if not logic_name:
            logic_name = '<template>new'

        if logic_name.startswith('<template>'):
            load_from_directory = self.logics_template_dir_name
            logic_name = logic_name[10:]
        else:
            load_from_directory = self.logics_directory_name

        sanitized_logic_name = self.__sanitize_file_name(logic_name)
        fn_xml = path.join(load_from_directory,
                           sanitized_logic_name + '.blockly')

        if not path.exists(fn_xml):
            self.logger.warning(
                f"Logic does not exist: requested logic_name = '{original_logic_name}' filename '{fn_xml}'")
            raise FileNotFoundError(logic_name)

        self.logger.debug(
            f"get_blockly_logic_file_name: logic_name = '{original_logic_name}' -> '{fn_xml}'")
        return fn_xml

    def save_logic(self, logic_name, python_code, blockly_xml):
        original_logic_name = logic_name
        sanitized_logic_name = self.__sanitize_file_name(logic_name)
        if self.logic_yaml_section_prefix != '':
            sanitized_logic_name = self.logic_yaml_section_prefix + sanitized_logic_name

        # prepare values from xml-data
        config_list, logic_active = self.__parse_blockly_xml_header(
            python_code, original_logic_name, sanitized_logic_name)

        python_file_name = self.logics_directory_name + sanitized_logic_name + ".py"
        blockly_file_name = self.logics_directory_name + sanitized_logic_name + ".blockly"

        self.logger.info(
            f"blockly_save_logic: saving blockly logic {sanitized_logic_name} as file {python_file_name} - (original name by user: {original_logic_name})")

        self.logger.debug(
            f"blockly_save_logic: SAVE PY blockly logic {sanitized_logic_name} = {python_file_name}\n '{python_code}'")
        with open(python_file_name, 'w') as python_file:
            python_file.write(python_code)

        self.logger.debug(
            f"blockly_save_logic: SAVE XML blockly logic {sanitized_logic_name} = {blockly_file_name}\n '{blockly_xml}'")
        xml = self.__pretty_print_xml(blockly_xml)
        with open(blockly_file_name, 'w') as blockly_file:
            blockly_file.write(xml)

        # actually update logic.yaml
        self.shng_logics_api.update_config_section(
            logic_active, sanitized_logic_name, config_list)

        # load logic into SHNG
        self.shng_logics_api.load_logic(sanitized_logic_name)

    def __parse_logic_header_from_blockly_code_header(self, config_line):
        self.logger.info(f"parse logic header config_line: |{config_line}|")
        section_name, logic_active_info, file_name_comment = config_line.split(
            '#')

        _, logic_active = logic_active_info.split(':')
        logic_active = Utils.to_bool(logic_active.strip(), False)

        self.logger.info(
            f"blockly_update_config: #comment# section = '{section_name}'")
        return (section_name, file_name_comment, logic_active)

    def __parse_trigger_header_from_blockly_code_header(self, config_line):
        self.logger.info(f"parse trigger header config_line: |{config_line}|")
        section_name, trigger_info, trigger_comment = config_line.split('#')

        trigger_key, trigger_value = trigger_info.split(':')
        trigger_key = trigger_key.strip()
        trigger_value = trigger_value.strip()

        self.logger.info(
            f"blockly_update_config: #trigger# section = '{section_name}'")
        return (section_name, trigger_key, trigger_value, trigger_comment)

    def __parse_blockly_xml_header(self, code, original_logic_name_by_user, sanitized_logic_name):
        """
        Fill configuration section in /etc/logic.yaml from header lines in generated code
        """
        logic_active = False
        config_list = []
        for line in code.splitlines():
            line = line.replace(
                original_logic_name_by_user.lower().replace(" ", "_"), sanitized_logic_name)
            if line.startswith('#comment#') and config_list == []:
                _, file_name_comment, logic_active = self.__parse_logic_header_from_blockly_code_header(
                    line[9:])
                config_list.append(
                    ['filename', sanitized_logic_name + ".py", file_name_comment])
            elif line.startswith('#trigger#'):
                _, trigger_key, trigger_value, trigger_comment = self.__parse_trigger_header_from_blockly_code_header(
                    line[9:])
                if config_list == []:
                    config_list.append(
                        ['filename', sanitized_logic_name + ".py", ''])
                config_list.append(
                    [trigger_key, trigger_value, trigger_comment])
            elif line.startswith('"""'):    # initial .rst-comment reached, stop scanning
                break
            else:                           # non-metadata lines between beginning of code and initial .rst-comment
                pass
        return (config_list, logic_active)
