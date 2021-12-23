from os import path
from lib.utils import Utils


class BlocklyToShngLogic():

    def __init__(self, logger, logics_directory_name, section_prefix):
        self.logger = logger
        self.logics_directory_name = logics_directory_name
        self.logics_template_dir_name = path.join(path.join(path.dirname(__file__), '..'), 'logic_templates')
        self.section_prefix = section_prefix

        self.logger.debug(f"Logics Directory: '{self.logics_directory_name}'")
        self.logger.debug(
            f"Template Directory: '{self.logics_template_dir_name}'")

    def __pretty_print_xml(self, xml_in):
        import xml.dom.minidom

        xml = xml.dom.minidom.parseString(xml_in)
        xml_out = xml.toprettyxml()
        return xml_out

    def __sanitize_file_name(self, raw_name):
        return raw_name.lower()

    def get_blockly_logic_file_name(self, logic_name=None):
        self.logger.debug(
            f"get_blockly_logic_file_name: logic_name = '{logic_name}'")

        if logic_name is None:
            fn_xml = path.join(self.logics_template_dir_name, 'new.blockly')
        else:
            fn_xml = path.join(self.logics_directory_name,
                               logic_name + '.blockly')
        self.logger.debug(
            f"get_blockly_logic_file_name: logic_name = '{logic_name}' -> '{fn_xml}'")
        return fn_xml

    def save_logic(self, logic_name, python_code, blockly_xml):
        logic_name = self.__sanitize_file_name(logic_name)

        python_file_name = self.logics_directory_name + logic_name + ".py"
        blockly_file_name = self.logics_directory_name + logic_name + ".blockly"

        self.logger.info(
            f"blockly_save_logic: saving blockly logic {logic_name} as file {python_file_name}")

        self.logger.debug(
            f"blockly_save_logic: SAVE PY blockly logic {logic_name} = {python_file_name}\n '{python_code}'")
        with open(python_file_name, 'w') as python_file:
            python_file.write(python_code)

        self.logger.debug(
            f"blockly_save_logic: SAVE XML blockly logic {logic_name} = {blockly_file_name}\n '{blockly_xml}'")
        xml = self.__pretty_print_xml(blockly_xml)
        with open(blockly_file_name, 'w') as blockly_file:
            blockly_file.write(xml)

        self.__blockly_update_config(python_code, logic_name)

        section = logic_name
        if self.section_prefix != '':
            section = self.section_prefix + section

        self.shng_logics_api.load_logic(section)

    def __blockly_update_config(self, code, name=''):
        """
        Fill configuration section in /etc/logic.yaml from header lines in generated code

        Method is called from blockly_save_logic()

        :param code: Python code of the logic
        :param name: name of configuration section, if ommited, the section name is read from the source code
        :type code: str
        :type name: str
        """
        section = ''
        active = False
        config_list = []
        for line in code.splitlines():
            if (line.startswith('#comment#')):
                if config_list == []:
                    sc, fn, ac, fnco = line[9:].split('#')
                    fnk, fnv = fn.split(':')
                    ack, acv = ac.split(':')
                    active = Utils.to_bool(acv.strip(), False)
                    if section == '':
                        section = sc
                        self.logger.info(
                            "blockly_update_config: #comment# section = '{}'".format(section))
                    config_list.append([fnk.strip(), fnv.strip(), fnco])
            elif line.startswith('#trigger#'):
                sc, fn, tr, co = line[9:].split('#')
                trk, trv = tr.split(':')
                if config_list == []:
                    fnk, fnv = fn.split(':')
                    fnco = ''
                    config_list.append([fnk.strip(), fnv.strip(), fnco])
                if section == '':
                    section = sc
                    self.logger.info(
                        "blockly_update_config: #trigger# section = '{}'".format(section))
                config_list.append([trk.strip(), trv.strip(), co])
            elif line.startswith('"""'):    # initial .rst-comment reached, stop scanning
                break
            else:                           # non-metadata lines between beginning of code and initial .rst-comment
                pass

        if section == '':
            section = name
        if self.section_prefix != '':
            section = self.section_prefix + section
        self.logger.info(
            "blockly_update_config: section = '{}'".format(section))

        self.shng_logics_api.update_config_section(
            active, section, config_list)
