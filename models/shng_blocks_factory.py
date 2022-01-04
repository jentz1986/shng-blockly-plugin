from xml.dom import minidom
from lib.model.smartplugin import SmartPlugin
from lib.plugin import Plugins
from lib.item import Items


class BlocklySeparator():

    def __init__(self, gap_size=8):
        self.gap_size = gap_size

    def get_xml(self, document):
        ele = document.createElement("sep")
        ele.setAttribute("gap", str(self.gap_size))
        textNode = document.createTextNode("-")
        ele.appendChild(textNode)
        return ele

    def get_dict_for_json(self):
        # Completely equal to XML
        return {"kind": "sep", "gap": str(self.gap_size)}

    def __repr__(self) -> str:
        return f'<sep gap="{self.gap_size}"></sep>'


class BlocklyField():

    def __init__(self, name, content):
        self.name = name
        self.content = content

    def get_xml(self, document):
        ele = document.createElement("field")
        ele.setAttribute("name", self.name)
        textNode = document.createTextNode(self.content)
        ele.appendChild(textNode)
        return ele

    def get_dict_for_json(self):
        return { self.name: { "name": self.content }} #sic!
        # TODO: Deal with it
        # return {"kind": "field", "ERROR": str(self.content)}

    def __repr__(self) -> str:
        return f'<field name="{self.name}">{self.content}</field>'


class BlocklyMutation():

    def __init__(self, mutators_dict):
        self.mutators = mutators_dict

    def get_xml(self, document):
        ele = document.createElement("mutation")
        for mutation_key in self.mutators:
            ele.setAttribute(mutation_key, str(self.mutators[mutation_key]))
        return ele

    def get_dict_for_json(self):
        # TODO: Deal with it
        return {"kind": "mutation"}

    def __repr__(self) -> str:
        start = '<mutation'
        for mutation_key in self.mutators:
            start += f' {mutation_key}="{self.mutators[mutation_key]}"'
        return start + '></mutation>'


class BlocklyCategory():

    def __init__(self, name, custom=None):
        self.blocks = None
        self.categories = None
        self.name = name
        self.custom = custom

    def has_blocks(self):
        if self.blocks:
            return True
        return False

    def number_of_blocks(self):
        if self.blocks:
            return len(self.blocks)
        return 0

    def has_children(self):
        if self.blocks or self.categories:
            return True
        return False

    def add_block(self, block_type):
        block = BlocklyBlock(block_type)
        if self.blocks is None:
            self.blocks = []
        self.blocks.append(block)
        return block

    def prepend_block_object(self, block):
        if self.blocks is None:
            self.blocks = []
        self.blocks.insert(0, block)

    def add_category(self, name):
        cat = BlocklyCategory(name)
        if self.categories is None:
            self.categories = []
        self.categories.append(cat)
        return cat

    def append_category(self, category_object):
        if self.categories is None:
            self.categories = []
        self.categories.append(category_object)

    def add_separator(self, gap_size=8):
        sep = BlocklySeparator(gap_size)
        if self.categories is None:
            self.categories = []
        self.categories.append(sep)
        return sep

    def get_xml(self, document):
        ele = document.createElement("category")
        ele.setAttribute("name", self.name)
        if self.custom:
            ele.setAttribute("custom", self.custom)
        if not self.blocks and not self.categories:
            textNode = document.createTextNode("-")
            ele.appendChild(textNode)
        if self.blocks:
            for block in self.blocks:
                ele.appendChild(block.get_xml(document))
        if self.categories:
            for cat in self.categories:
                ele.appendChild(cat.get_xml(document))
        return ele

    def get_dict_for_json(self):
        # Completely equal to XML
        ret_dict = {"kind": "category", "name": self.name}
        if self.custom:
            ret_dict["custom"] = self.custom
        if self.blocks or self.categories:
            ret_dict["contents"] = []
            if self.blocks:
                for block in self.blocks:
                    ret_dict["contents"].append(block.get_dict_for_json())
            if self.categories:
                for cat in self.categories:
                    ret_dict["contents"].append(cat.get_dict_for_json())
        return ret_dict

    def __repr__(self) -> str:
        start = f'<category name="{self.name}"'
        if self.custom:
            start += f' custom="{self.custom}"'
        start += '>'
        if self.blocks:
            for block in self.blocks:
                start += repr(block)
        if self.categories:
            for cat in self.categories:
                start += repr(cat)
        start += '</category>'
        return start


class BlocklyBlock():

    def __init__(self, block_type, name=None):
        self.block_type = block_type
        self.name = name
        self.values = None
        self.fields = None
        self.mutations = None

    def add_value(self, name):
        if self.values is None:
            self.values = []
        val = BlocklyValue(name)
        self.values.append(val)
        return val

    def add_field(self, name, value):
        if self.fields is None:
            self.fields = []
        val = BlocklyField(name, value)
        self.fields.append(val)
        return val

    def add_mutation(self, mutators_list):
        if self.mutations is None:
            self.mutations = []
        val = BlocklyMutation(mutators_list)
        self.mutations.append(val)
        return val

    def get_xml(self, document):
        ele = document.createElement("block")
        ele.setAttribute("type", self.block_type)
        if self.name:
            ele.setAttribute("name", self.name)
        if not(self.fields) and not(self.values) and not(self.mutations):
            textNode = document.createTextNode("-")
            ele.appendChild(textNode)
        if self.fields:
            for field in self.fields:
                ele.appendChild(field.get_xml(document))
        if self.values:
            for value in self.values:
                ele.appendChild(value.get_xml(document))
        if self.mutations:
            for mutation in self.mutations:
                ele.appendChild(mutation.get_xml(document))
        return ele

    def get_dict_for_json(self):
        ret_dict = {"kind": "block", "type": self.block_type}
        if self.name:
            ret_dict["name"] = self.name
        ret_dict["blockxml"] = repr(self).replace('"', "'")
        # TODO: Add fields
        # TODO: add values
        # TODO: add mutations
        return ret_dict

    def __repr__(self) -> str:
        start = f'<block name="{self.name}" type="{self.block_type}">'
        if self.values:
            for block in self.values:
                start += repr(block)
        if self.fields:
            for cat in self.fields:
                start += repr(cat)
        if self.mutations:
            for cat in self.mutations:
                start += repr(cat)
        start += '</block>'
        return start


class BlocklyValue():

    def __init__(self, name):
        self.blocks = None
        self.name = name

    def add_block(self, block_type):
        block = BlocklyBlock(block_type)
        if self.blocks is None:
            self.blocks = []
        self.blocks.append(block)
        return block

    def get_xml(self, document):
        ele = document.createElement("value")
        ele.setAttribute("name", self.name)
        if self.blocks:
            for block in self.blocks:
                ele.appendChild(block.get_xml(document))
        return ele

    def get_dict_for_json(self):
        ret_dict = {"kind": "value", "name": self.name}
        # TODO: Add child blocks
        return ret_dict

    def __repr__(self) -> str:
        start = f'<value name="{self.name}">'
        if self.blocks:
            for block in self.blocks:
                start += repr(block)
        start += '</value>'
        return start


class ShngItemsToBlockly():

    def __init__(self):
        self.sh_items_api = None

    def __remove_prefix(self, string, prefix):
        if string.startswith(prefix):
            return string[len(prefix):]
        return string

    def __create_root_category(self):
        if self.sh_items_api is None:
            self.sh_items_api = Items.get_instance()

        root_items = filter(lambda i: i._path.find('.') == -1 and i._path not in ['env_daily', 'env_init', 'env_loc', 'env_stat'],
                            sorted(self.sh_items_api.return_items(),
                                   key=lambda k: str.lower(k['_path']), reverse=False))

        root = self.__iterate_items(root_items, "SmartHomeNG Items")
        root.add_block("sh_item_get")
        root.add_block("sh_item_set")
        root.add_block("sh_item_hasattr")

        return root

    def __create_item_block(self, item, name):
        new_block = BlocklyBlock("sh_item_obj", item._path)
        new_block.add_field("N", name)
        new_block.add_field("P", item._path)
        new_block.add_field("T", item.type())
        return new_block

    def __iterate_items(self, items, name, prefix_to_cut=""):
        category = BlocklyCategory(name)

        for item in items:
            shortname = self.__remove_prefix(item.path(), prefix_to_cut + '.')
            children = sorted(item.return_children(
            ), key=lambda k: str.lower(k['_path']), reverse=False)
            if len(children) > 0:
                child_category = self.__iterate_items(
                    children, shortname, item._path)
                if child_category:
                    if (item.type() != 'foo') or (item() != None):
                        this_item = self.__create_item_block(item, shortname)
                        child_category.prepend_block_object(this_item)
                    count_of_child_blocks = child_category.number_of_blocks()
                    child_category.name = f"{shortname} ({count_of_child_blocks})"
                    category.append_category(child_category)
            else:
                if (item.type() != 'foo') or (item() != None):
                    category.prepend_block_object(
                        self.__create_item_block(item, shortname))

        if not category.has_children():
            return None

        return category

    def get_dict_for_json(self):
        root_cat = self.__create_root_category()
        ret_dict = root_cat.get_dict_for_json()
        return ret_dict

    def get_xml(self, document):
        root_cat = self.__create_root_category()
        return root_cat.get_xml(document)

    def get_xml_string(self):
        document = minidom.Document()
        ele = self.get_xml(document)
        document.appendChild(ele)
        return document.toprettyxml(indent="    ")


class ShngPluginFunctionsToBlockly():

    def __init__(self):
        self.plugins = None
        self.plugin_functions_list = []

    def __build_plugin_functions_list(self):
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

    def __create_root_category(self):
        category = BlocklyCategory("SmarthomeNG Plugins")
        return category

    def get_xml(self, document):
        self.__build_plugin_functions_list()
        root_cat = self.__create_root_category()
        return root_cat.get_xml(document)

    def get_xml_string(self):
        document = minidom.Document()
        ele = self.get_xml(document)
        document.appendChild(ele)
        return document.toprettyxml(indent="    ")


class ShngBlockFactory():

    def __init__(self):
        self.items_to_block = ShngItemsToBlockly()
        self.plugin_functions_to_blocks = ShngPluginFunctionsToBlockly()

    def tree_generator(self):
        yield self.get_blocks_shng_logic()
        yield self.get_shng_library()
        yield self.items_to_block
        yield BlocklySeparator()
        yield self.get_blocks_if()
        yield self.get_blocks_boolean()
        yield self.get_blocks_loops()
        # Math
        # Text
        # Lists
        # Colour
        yield BlocklyCategory("Variables", "VARIABLE")
        yield BlocklyCategory("Functions", "PROCEDURE")

    def get_blocks_shng_logic(self):
        root_cat = BlocklyCategory("SmartHomeNG Logic")
        root_cat.add_block("sh_logic_main")
        root_cat.add_block("sh_trigger_item").add_value("TRIG_ITEM")
        root_cat.add_block("sh_trigger_cycle")
        root_cat.add_block("sh_trigger_sun")
        root_cat.add_block("sh_trigger_daily")
        root_cat.add_block("sh_trigger_init")
        return root_cat

    def get_shng_library(self):
        root_cat = BlocklyCategory("SmartHomeNG Library")
        time_cat = root_cat.add_category("Time")
        time_cat.add_block("shtime_now")
        time_cat.add_block("shtime_time")
        time_cat.add_block("shtime_sunpos")
        time_cat.add_block("shtime_moon")
        time_cat.add_block("shtime_auto")
        tool_cat = root_cat.add_category("Tools")
        tool_cat.add_block("shtools_logger").add_value(
            "LOGTEXT").add_block("text")
        dew_point = tool_cat.add_block("shtools_dewpoint")
        dew_point.add_value("HUM").add_block(
            "math_number").add_field("NUM", "42")
        dew_point.add_value("TEMP").add_block(
            "math_number").add_field("NUM", "21")
        tool_cat.add_block("shtools_fetchurl")
        tool_cat.add_block("shtools_fetchurl2")
        return root_cat

    def get_blocks_if(self):
        root_cat = BlocklyCategory("Logics")
        root_cat.add_block("controls_if")
        root_cat.add_block("controls_if").add_mutation({"else": "1"})
        root_cat.add_block("controls_if").add_mutation(
            {"else": "1", "elseif": "1"})
        return root_cat

    def get_blocks_boolean(self):
        root_cat = BlocklyCategory("Boolean")
        root_cat.add_block("logic_compare")
        root_cat.add_block("logic_operation")
        root_cat.add_block("logic_negate")
        root_cat.add_block("logic_boolean")
        root_cat.add_block("logic_null")
        root_cat.add_block("logic_ternary")
        return root_cat

    def get_blocks_loops(self):
        root_cat = BlocklyCategory("Loops")
        root_cat.add_block("controls_repeat_ext").add_value(
            "TIMES").add_block("math_number").add_field("NUM", "10")
        root_cat.add_block("controls_whileUntil")
        for_b = root_cat.add_block("controls_for")
        for_b.add_field("VAR", "i")
        for_b.add_value("FROM").add_block("math_number").add_field("NUM", "1")
        for_b.add_value("TO").add_block("math_number").add_field("NUM", "1")
        for_b.add_value("BY").add_block("math_number").add_field("NUM", "1")
        root_cat.add_block("controls_forEach")
        root_cat.add_block("controls_flow_statements")
        return root_cat

    def get_toolbox_xml_string(self):
        doc = minidom.Document()
        root = doc.createElement("xml")
        for line in self.tree_generator():
            root.appendChild(line.get_xml(doc))
        doc.appendChild(root)
        return doc.toprettyxml(indent="    ")

    def get_toolbox_dict_for_json(self):
        contents = []
        for line in self.tree_generator():
            contents.append(line.get_dict_for_json())
        return {"kind": "categoryToolbox", "contents": contents}

    """
    <category name="Math">
        <block type="math_number"></block>
        <block type="math_arithmetic"></block>
        <block type="math_single"></block>
        <block type="math_trig"></block>
        <block type="math_constant"></block>
        <block type="math_number_property"></block>
        <block type="math_change">
            <value name="DELTA">
                <block type="math_number">
                    <field name="NUM">1</field>
                </block>
            </value>
        </block>
        <block type="math_round"></block>
        <block type="math_on_list"></block>
        <block type="math_modulo"></block>
        <block type="math_constrain">
            <value name="LOW">
                <block type="math_number">
                    <field name="NUM">1</field>
                </block>
            </value>
            <value name="HIGH">
                <block type="math_number">
                    <field name="NUM">100</field>
                </block>
            </value>
        </block>
        <block type="math_random_int">
            <value name="FROM">
                <block type="math_number">
                    <field name="NUM">1</field>
                </block>
            </value>
            <value name="TO">
                <block type="math_number">
                    <field name="NUM">100</field>
                </block>
            </value>
        </block>
        <block type="math_random_float"></block>
    </category>
    <category name="Text">
        <block type="text"></block>
        <block type="text_join"></block>
        <block type="text_append">
            <value name="TEXT">
                <block type="text"></block>
            </value>
        </block>
        <block type="text_length"></block>
        <block type="text_isEmpty"></block>
        <block type="text_indexOf">
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" class="textVar">...</field>
                </block>
            </value>
        </block>
        <block type="text_charAt">
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" class="textVar">...</field>
                </block>
            </value>
        </block>
        <block type="text_getSubstring">
            <value name="STRING">
                <block type="variables_get">
                    <field name="VAR" class="textVar">...</field>
                </block>
            </value>
        </block>
        <block type="text_changeCase"></block>
        <block type="text_trim"></block>
        <block type="text_print"></block>
        <block type="text_prompt_ext">
            <value name="TEXT">
                <block type="text"></block>
            </value>
        </block>
    </category>
    <category name="Lists">
        <block type="lists_create_empty"></block>
        <block type="lists_create_with"></block>
        <block type="lists_repeat">
            <value name="NUM">
                <block type="math_number">
                    <field name="NUM">5</field>
                </block>
            </value>
        </block>
        <block type="lists_length"></block>
        <block type="lists_isEmpty"></block>
        <block type="lists_indexOf">
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" class="listVar">...</field>
                </block>
            </value>
        </block>
        <block type="lists_getIndex">
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" class="listVar">...</field>
                </block>
            </value>
        </block>
        <block type="lists_setIndex">
            <value name="LIST">
                <block type="variables_get">
                    <field name="VAR" class="listVar">...</field>
                </block>
            </value>
        </block>
        <block type="lists_getSublist">
            <value name="LIST">
                <block type="variables_get">
                    <field name="VAR" class="listVar">...</field>
                </block>
            </value>
        </block>
    </category>
    <category name="Colour">
        <block type="colour_picker"></block>
        <block type="colour_random"></block>
        <block type="colour_rgb">
            <value name="RED">
                <block type="math_number">
                    <field name="NUM">100</field>
                </block>
            </value>
            <value name="GREEN">
                <block type="math_number">
                    <field name="NUM">50</field>
                </block>
            </value>
            <value name="BLUE">
                <block type="math_number">
                    <field name="NUM">0</field>
                </block>
            </value>
        </block>
        <block type="colour_blend">
            <value name="COLOUR1">
                <block type="colour_picker">
                    <field name="COLOUR">#ff0000</field>
                </block>
            </value>
            <value name="COLOUR2">
                <block type="colour_picker">
                    <field name="COLOUR">#3333ff</field>
                </block>
            </value>
            <value name="RATIO">
                <block type="math_number">
                    <field name="NUM">0.5</field>
                </block>
            </value>
        </block>
    </category>
    """
