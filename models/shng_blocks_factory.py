from xml.dom.minidom import Element, Document
from lib.model.smartplugin import SmartPlugin
from lib.plugin import Plugins
from lib.item import Items


class BlocklySeparator():

    def __init__(self, gap_size=8):
        self.gap_size = gap_size

    def get_xml(self, document) -> Element:
        ele = document.createElement("sep")
        ele.setAttribute("gap", str(self.gap_size))
        textNode = document.createTextNode("-")
        ele.appendChild(textNode)
        return ele

    def get_dict_for_json(self) -> dict:
        # Completely equal to XML
        return {"kind": "sep", "gap": str(self.gap_size)}

    def __repr__(self) -> str:
        return f'<sep gap="{self.gap_size}"></sep>'


class BlocklyField():

    def __init__(self, name, content, class_=None):
        self.name = name
        self.content = content
        self.class_ = class_

    def get_xml(self, document) -> Element:
        ele = document.createElement("field")
        ele.setAttribute("name", self.name)
        textNode = document.createTextNode(self.content)
        ele.appendChild(textNode)
        return ele

    def get_dict_for_json(self) -> dict:
        raise NotImplementedError(
            "Blockly does not support parsing fields from JSON yet")

    def __repr__(self) -> str:
        start = f'<field name="{self.name}"'
        if self.class_:
            start += f" class=\"{self.class_}\""
        return start + f'>{self.content}</field>'


class BlocklyMutation():

    def __init__(self, mutators_dict):
        self.mutators = mutators_dict

    def get_xml(self, document) -> Element:
        ele = document.createElement("mutation")
        for mutation_key in self.mutators:
            ele.setAttribute(mutation_key, str(self.mutators[mutation_key]))
        return ele

    def get_dict_for_json(self) -> dict:
        raise NotImplementedError(
            "Blockly does not support parsing mutations from JSON yet")

    def __repr__(self) -> str:
        start = '<mutation'
        for mutation_key in self.mutators:
            start += f' {mutation_key}="{self.mutators[mutation_key]}"'
        return start + '></mutation>'


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

    def get_xml(self, document) -> Element:
        ele = document.createElement("value")
        ele.setAttribute("name", self.name)
        if self.blocks:
            for block in self.blocks:
                ele.appendChild(block.get_xml(document))
        return ele

    def get_dict_for_json(self):
        raise NotImplementedError(
            "Blockly does not support parsing values from JSON yet")

    def __repr__(self) -> str:
        start = f'<value name="{self.name}">'
        if self.blocks:
            for block in self.blocks:
                start += repr(block)
        start += '</value>'
        return start


class BlocklyBlock():

    def __init__(self, block_type, name=None):
        self.block_type = block_type
        self.name = name
        self.values = None
        self.fields = None
        self.mutations = None

    def add_value(self, name) -> BlocklyValue:
        if self.values is None:
            self.values = []
        val = BlocklyValue(name)
        self.values.append(val)
        return val

    def add_field(self, name, value, class_=None) -> BlocklyField:
        if self.fields is None:
            self.fields = []
        val = BlocklyField(name, value, class_)
        self.fields.append(val)
        return val

    def add_mutation(self, mutators_list) -> BlocklyMutation:
        if self.mutations is None:
            self.mutations = []
        val = BlocklyMutation(mutators_list)
        self.mutations.append(val)
        return val

    def get_xml(self, document) -> Element:
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

    def get_dict_for_json(self) -> dict:
        ret_dict = {"kind": "block", "type": self.block_type}
        if self.name:
            ret_dict["name"] = self.name
        ret_dict["blockxml"] = repr(self).replace('"', "'")
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


class BlocklyCategory():

    def __init__(self, name, custom=None):
        self.blocks = None
        self.categories = None
        self.name = name
        self.custom = custom

    def has_blocks(self) -> bool:
        if self.blocks:
            return True
        return False

    def number_of_blocks(self) -> int:
        if self.blocks:
            return len(self.blocks)
        return 0

    def has_children(self) -> bool:
        if self.blocks or self.categories:
            return True
        return False

    def add_block(self, block_type) -> BlocklyBlock:
        block = BlocklyBlock(block_type)
        if self.blocks is None:
            self.blocks = []
        self.blocks.append(block)
        return block

    def prepend_block_object(self, block: BlocklyBlock):
        if self.blocks is None:
            self.blocks = []
        self.blocks.insert(0, block)

    def add_category(self, name: str):
        cat = BlocklyCategory(name)
        if self.categories is None:
            self.categories = []
        self.categories.append(cat)
        return cat

    def append_category(self, category_object):
        if self.categories is None:
            self.categories = []
        self.categories.append(category_object)

    def add_separator(self, gap_size=8) -> BlocklySeparator:
        sep = BlocklySeparator(gap_size)
        if self.categories is None:
            self.categories = []
        self.categories.append(sep)
        return sep

    def get_xml(self, document: Document) -> Element:
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


class ShngItemsToBlockly():

    def __init__(self, root_name):
        self.sh_items_api = None
        self.__root_name = root_name

    def __remove_prefix(self, string, prefix) -> str:
        if string.startswith(prefix):
            return string[len(prefix):]
        return string

    def __create_root_category(self) -> BlocklyCategory:
        if self.sh_items_api is None:
            self.sh_items_api = Items.get_instance()

        root_items = filter(lambda i: i._path.find('.') == -1 and i._path not in ['env_daily', 'env_init', 'env_loc', 'env_stat'],
                            sorted(self.sh_items_api.return_items(),
                                   key=lambda k: str.lower(k['_path']), reverse=False))

        root = self.__iterate_items(root_items, self.__root_name)
        root.add_block("sh_item_get")
        root.add_block("sh_item_set")
        root.add_block("sh_item_hasattr")

        return root

    def __create_item_block(self, item, name: str) -> BlocklyBlock:
        new_block = BlocklyBlock("sh_item_obj", item.path())
        new_block.add_field("N", name)
        new_block.add_field("P", item.path())
        new_block.add_field("T", item.type())
        return new_block

    def __iterate_items(self, items, name: str, prefix_to_cut: str = ""):
        category = BlocklyCategory(name)

        for item in items:
            shortname = self.__remove_prefix(item.path(), prefix_to_cut + '.')
            children = sorted(item.return_children(
            ), key=lambda k: str.lower(k['_path']), reverse=False)
            if len(children) > 0:
                child_category = self.__iterate_items(
                    children, shortname, item.path())
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

    def get_dict_for_json(self) -> dict:
        root_cat = self.__create_root_category()
        ret_dict = root_cat.get_dict_for_json()
        return ret_dict

    def get_xml(self, document: Document) -> Element:
        root_cat = self.__create_root_category()
        return root_cat.get_xml(document)


class ShngPluginFunctionsToBlockly():

    def __init__(self, root_name):
        self.plugins = None
        self.__root_name = root_name
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

    def __create_root_category(self) -> BlocklyCategory:
        category = BlocklyCategory(self.__root_name)
        return category

    def get_xml(self, document: Document) -> Element:
        self.__build_plugin_functions_list()
        root_cat = self.__create_root_category()
        return root_cat.get_xml(document)

    def get_dict_for_json(self) -> dict:
        self.__build_plugin_functions_list()
        root_cat = self.__create_root_category()
        ret_dict = root_cat.get_dict_for_json()
        return ret_dict


class ShngBlockFactory():

    def __init__(self, translation_function):
        self.__items_to_block = None
        self.__plugin_functions_to_blocks = None
        self.translate = translation_function

    def __tree_generator(self):
        yield self.__get_blocks_shng_logic()
        yield self.__get_blocks_shng_tools()
        yield self.__get_blocks_shng_plugin_functions()
        yield self.__get_blocks_shng_items()
        yield BlocklySeparator()
        yield self.__get_blocks_if()
        yield self.__get_blocks_boolean()
        yield self.__get_blocks_loops()
        yield self.__get_blocks_math()
        yield self.__get_blocks_text()
        yield self.__get_blocks_lists()
        yield self.__get_blocks_colours()
        yield BlocklyCategory(self.translate("Variables"), "VARIABLE")
        yield BlocklyCategory(self.translate("Functions"), "PROCEDURE")

    def __get_blocks_shng_logic(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("SmartHomeNG Logic"))
        root_cat.add_block("sh_logic_main")
        root_cat.add_block("sh_trigger_item").add_value("TRIG_ITEM")
        root_cat.add_block("sh_trigger_cycle")
        root_cat.add_block("sh_trigger_sun")
        root_cat.add_block("sh_trigger_daily")
        root_cat.add_block("sh_trigger_init")
        return root_cat

    def __get_blocks_shng_tools(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("SmartHomeNG Tools"))

        time_cat = root_cat.add_category(self.translate("Time"))
        time_cat.add_block("shtime_now")
        time_cat.add_block("shtime_time")
        time_cat.add_block("shtime_sunpos")
        time_cat.add_block("shtime_moon")
        time_cat.add_block("shtime_auto")

        tool_cat = root_cat.add_category(self.translate("Tools"))
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

    def __get_blocks_shng_plugin_functions(self) -> BlocklyCategory:
        if self.__plugin_functions_to_blocks is None:
            self.__plugin_functions_to_blocks = ShngPluginFunctionsToBlockly(
                self.translate("SmartHomeNG Plugin-Functions"))
        return self.__plugin_functions_to_blocks

    def __get_blocks_shng_items(self) -> BlocklyCategory:
        if self.__items_to_block is None:
            self.__items_to_block = ShngItemsToBlockly(
                self.translate("SmartHomeNG Items"))
        return self.__items_to_block

    def __get_blocks_if(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("IfElse"))
        root_cat.add_block("controls_if")
        root_cat.add_block("controls_if").add_mutation({"else": "1"})
        root_cat.add_block("controls_if").add_mutation(
            {"else": "1", "elseif": "1"})
        return root_cat

    def __get_blocks_boolean(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Boolean"))
        root_cat.add_block("logic_compare")
        root_cat.add_block("logic_operation")
        root_cat.add_block("logic_negate")
        root_cat.add_block("logic_boolean")
        root_cat.add_block("logic_null")
        root_cat.add_block("logic_ternary")
        return root_cat

    def __get_blocks_loops(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Loops"))
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

    def __get_blocks_math(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Math"))
        root_cat.add_block("math_number")
        root_cat.add_block("math_arithmetic")
        root_cat.add_block("math_single")
        root_cat.add_block("math_trig")
        root_cat.add_block("math_constant")
        root_cat.add_block("math_number_property")
        root_cat.add_block("math_change").add_value(
            "DELTA").add_block("math_number").add_field("NUM", 1)
        root_cat.add_block("math_round")
        root_cat.add_block("math_on_list")
        root_cat.add_block("math_modulo")
        constr = root_cat.add_block("math_constrain")
        constr.add_value("LOW").add_block("math_number").add_field("NUM", 1)
        constr.add_value("HIGH").add_block("math_number").add_field("NUM", 100)
        random = root_cat.add_block("math_random_int")
        random.add_value("FROM").add_block("math_number").add_field("NUM", 1)
        random.add_value("TO").add_block("math_number").add_field("NUM", 100)
        root_cat.add_block("math_random_float")
        return root_cat

    def __get_blocks_text(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Text"))
        root_cat.add_block("text")
        root_cat.add_block("text_join")
        root_cat.add_block("text_append").add_value("TEXT").add_block("text")
        root_cat.add_block("text_length")
        root_cat.add_block("text_isEmpty")
        root_cat.add_block("text_indexOf").add_value("VALUE").add_block(
            "variables_get").add_field("VAR", "...", class_="textVar")
        root_cat.add_block("text_charAt").add_value("VALUE").add_block(
            "variables_get").add_field("VAR", "...", class_="textVar")
        root_cat.add_block("text_getSubstring").add_value("STRING").add_block(
            "variables_get").add_field("VAR", "...", class_="textVar")
        root_cat.add_block("text_changeCase")
        root_cat.add_block("text_trim")
        root_cat.add_block("text_print")
        root_cat.add_block("text_prompt_ext").add_value(
            "TEXT").add_block("text")
        return root_cat

    def __get_blocks_lists(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Lists"))
        root_cat.add_block("lists_create_empty")
        root_cat.add_block("lists_create_with")
        root_cat.add_block("lists_repeat").add_value(
            "NUM").add_block("math_number").add_field("NUM", 5)
        root_cat.add_block("lists_length")
        root_cat.add_block("lists_isEmpty")
        root_cat.add_block("lists_indexOf").add_value("VALUE").add_block(
            "variables_get").add_field("VAR", "...", class_="listVar")
        root_cat.add_block("lists_getIndex").add_value("VALUE").add_block(
            "variables_get").add_field("VAR", "...", class_="listVar")
        root_cat.add_block("lists_setIndex").add_value("LIST").add_block(
            "variables_get").add_field("VAR", "...", class_="listVar")
        root_cat.add_block("lists_getSublist").add_value("LIST").add_block(
            "variables_get").add_field("VAR", "...", class_="listVar")
        return root_cat

    def __get_blocks_colours(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Colours"))
        root_cat.add_block("colour_picker")
        rgb = root_cat.add_block("colour_rgb")
        rgb.add_value("RED").add_block("math_number").add_field("NUM", 100)
        rgb.add_value("GREEN").add_block("math_number").add_field("NUM", 50)
        rgb.add_value("BLUE").add_block("math_number").add_field("NUM", 0)
        blender = root_cat.add_block("colour_blend")
        blender.add_value("COLOUR1").add_block(
            "colour_picker").add_field("COLOUR", "#ff0000")
        blender.add_value("COLOUR2").add_block(
            "colour_picker").add_field("COLOUR", "#3333ff")
        blender.add_value("RATIO").add_block(
            "math_number").add_field("NUM", 0.5)

        return root_cat

    def get_toolbox_xml_string(self) -> str:
        doc = Document()
        root = doc.createElement("xml")
        for line in self.__tree_generator():
            root.appendChild(line.get_xml(doc))
        doc.appendChild(root)
        return doc.toprettyxml(indent="    ")

    def get_toolbox_dict_for_json(self) -> dict:
        contents = []
        for line in self.__tree_generator():
            contents.append(line.get_dict_for_json())
        return {"kind": "categoryToolbox", "contents": contents}
