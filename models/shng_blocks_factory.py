from xml.dom.minidom import Element, Document
from lib.model.smartplugin import SmartPlugin
from lib.plugin import Plugins
from lib.item import Items


def translate_to_blockly_value_type(raw_type):
    if raw_type is None:
        return None
    if raw_type == "bool":
        return "Boolean"
    if raw_type.startswith("list"):
        return "Array"
    if raw_type.startswith("dict"):
        return "Array"
    if raw_type == "int":
        return "Number"
    if raw_type == "num":
        return "Number"
    if raw_type == "str":
        return "String"
    if raw_type == "mac":
        return "String"
    if raw_type == "knx_ga":
        return "String"
    if raw_type == "void":
        return "void"


def translate_to_blockly_shadow_type(value_type, default_value=None):
    if value_type == "Boolean":
        return ("logic_boolean", None)
    elif value_type == "Array":
        return ("lists_create_empty", None)
    elif value_type == "Number":
        if default_value is not None:
            return ("math_number", "NUM")
        else:
            return ("math_number", None)
    elif value_type == "String":
        if default_value is None:
            return ("text", None)
        else:
            if default_value == '<<NULL>>':
                return ("logic_null", None)
            else:
                return ("text", "TEXT")
    return (None, None)


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
        textNode = document.createTextNode(str(self.content))
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


class BlocklyShadow():

    def __init__(self, block_type):
        self.block_type = block_type
        self.values = None
        self.fields = None
        self.mutations = None

    def add_value(self, name):
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
        ele = document.createElement("shadow")
        ele.setAttribute("type", self.block_type)
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
        raise NotImplementedError(
            "Blockly does not support parsing values from JSON yet")

    def __repr__(self) -> str:
        start = f'<shadow type="{self.block_type}">'
        if self.values:
            for block in self.values:
                start += repr(block)
        if self.fields:
            for cat in self.fields:
                start += repr(cat)
        if self.mutations:
            for cat in self.mutations:
                start += repr(cat)
        start += '</shadow>'
        return start


class BlocklyValue():

    def __init__(self, name):
        self.blocks = None
        self.name = name

    def add_block(self, block_type):
        if isinstance(block_type, BlocklyBlock):
            block = block_type
        else:
            block = BlocklyBlock(block_type)
        if self.blocks is None:
            self.blocks = []
        self.blocks.append(block)
        return block

    def add_shadow(self, primitive_type) -> BlocklyField:
        shadow = BlocklyShadow(primitive_type)
        if self.blocks is None:
            self.blocks = []
        self.blocks.append(shadow)
        return shadow

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
        self.__writable_primitive_type_for_item = None

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
        if name == "T" and self.block_type == "sh_item_obj":
            self.__writable_primitive_type_for_item = value
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

    def _get_writable_primitive_type_for_item(self):
        return self.__writable_primitive_type_for_item

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

    def add_category(self, name):
        if isinstance(name, BlocklyCategory):
            cat = name
        else:
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
    __sh_items_api = None

    def wrap_in_setter(block_to_be_wrapped):
        wrapper = BlocklyBlock("shng_item_set")
        wrapper.add_value("ITEMOBJECT").add_block(block_to_be_wrapped)
        item_type = block_to_be_wrapped._get_writable_primitive_type_for_item()
        wrapper.add_field("ITEMTYPE", item_type)
        prim_type = translate_to_blockly_value_type(item_type)
        shadow_type, _ = translate_to_blockly_shadow_type(prim_type)
        wrapper.add_value("VALUE").add_shadow(shadow_type)
        return wrapper

    def wrap_in_getter(block_to_be_wrapped):
        wrapper = BlocklyBlock("shng_item_get")
        wrapper.add_value("ITEMOBJECT").add_block(block_to_be_wrapped)
        wrapper.add_field("PROP", "value")
        wrapper.add_field("ITEMTYPE",
                          block_to_be_wrapped._get_writable_primitive_type_for_item())
        return wrapper

    def wrap_trigger(block_to_be_wrapped):
        wrapper = BlocklyBlock("sh_trigger_item")
        wrapper.add_value("TRIG_ITEM").add_block(block_to_be_wrapped)
        return wrapper

    def __init__(self):
        self.__items_cache = None
        pass

    def __remove_prefix(self, string, prefix) -> str:
        if string.startswith(prefix):
            return string[len(prefix):]
        return string

    def __create_root_category(self, category_name, wrapping_function) -> BlocklyCategory:
        if ShngItemsToBlockly.__sh_items_api is None:
            ShngItemsToBlockly.__sh_items_api = Items.get_instance()
        if self.__items_cache is None:
            self.__items_cache = list(filter(lambda i: i.path().find('.') == -1 and i.path() not in ['env_daily', 'env_init', 'env_loc', 'env_stat'],
                                             sorted(self.__sh_items_api.return_items(),
                                                    key=lambda k: str.lower(k['_path']), reverse=False)))

        root = self.__iterate_items(
            self.__items_cache, category_name, prefix_to_cut="", wrapping_function=wrapping_function)
        return root

    def __create_item_block(self, item, name: str, wrapping_function) -> BlocklyBlock:
        new_block = BlocklyBlock("sh_item_obj", item.path())
        new_block.add_field("N", name)
        new_block.add_field("P", item.path())
        new_block.add_field("T", item.type())
        return wrapping_function(new_block)

    def __iterate_items(self, items, name: str, prefix_to_cut: str, wrapping_function):
        category = BlocklyCategory(name)

        for item in items:
            shortname = self.__remove_prefix(item.path(), prefix_to_cut + '.')
            children = sorted(item.return_children(
            ), key=lambda k: str.lower(k['_path']), reverse=False)
            if len(children) > 0:
                child_category = self.__iterate_items(
                    children, shortname, item.path(), wrapping_function)
                if child_category:
                    if (item.type() != 'foo') or (item() != None):
                        this_item = self.__create_item_block(
                            item, shortname, wrapping_function)
                        child_category.prepend_block_object(this_item)
                    count_of_child_blocks = child_category.number_of_blocks()
                    child_category.name = f"{shortname} ({count_of_child_blocks})"
                    category.append_category(child_category)
            else:
                if (item.type() != 'foo') or (item() != None):
                    category.prepend_block_object(
                        self.__create_item_block(item, shortname, wrapping_function))

        if not category.has_children():
            return None

        return category

    def get(self, root_cat_name: str, wrapping_function) -> BlocklyCategory:
        root_cat = self.__create_root_category(
            root_cat_name, wrapping_function)
        root_cat.name = root_cat_name
        return root_cat


class ShngPluginFunctionsToBlockly():

    def __init__(self, root_name, language='en'):
        self.plugins = None
        self.__root_name = root_name
        self.plugin_functions = {}
        self.param_types = set()
        self.language = language

    def __simplify_types_for_blockly(self, raw_type: str, name: str = None):
        to_return = translate_to_blockly_value_type(raw_type)
        if to_return:
            return to_return
        if name:
            if "item" in name.lower() and raw_type == "foo":
                return "shItemType"
        return "foo"

    def __get_function_params_info(self, func_param_yaml):
        if not (func_param_yaml is None):
            for par in func_param_yaml:
                p_name = str(par)
                p_type = None
                p_default = None
                if func_param_yaml[par].get('type', None) != None:
                    p_type = str(func_param_yaml[par].get('type', None))
                    self.param_types.add(p_type)
                if func_param_yaml[par].get('default', None) != None:
                    p_default = str(
                        func_param_yaml[par].get('default', None))
                    if func_param_yaml[par].get('type', 'foo') == 'str':
                        if p_default == 'None*':
                            p_default = 'None'
                        if p_default == 'None':
                            p_default = '<<NULL>>'
                        else:
                            p_default = p_default
                yield {"p_name": p_name, "p_type_raw": p_type, "p_type": self.__simplify_types_for_blockly(p_type, p_name), "p_default": p_default}

    def __build_plugin_function_info(self, metadata_info):
        # Stolen from lib/metadata.py#L196...
        if metadata_info.plugin_functions is not None:
            for f in sorted(metadata_info.plugin_functions):
                func_param_yaml = metadata_info.plugin_functions[f].get(
                    'parameters', None)
                f_type = metadata_info.plugin_functions[f].get(
                    'type', 'void')
                f_descr = metadata_info.plugin_functions[f].get(
                    'description', None)

                params = self.__get_function_params_info(func_param_yaml)

                yield {"m_name": f, "m_description": f_descr,
                       "m_pars": list(params), "m_ret_type_raw": f_type,
                       "m_ret_type": self.__simplify_types_for_blockly(f_type)}

    def __build_plugin_functions_list(self):
        # Stolen from /modules/admin/api_plugins.py#L500-L519
        # rf. https://github.com/smarthomeNG/smarthome/blob/301e4968483079098b01f1e6853c9f358ca6f552/modules/admin/api_plugins.py#L500-L519
        if self.plugins is None:
            self.plugins = Plugins.get_instance()
        self.plugin_functions_list = []
        for x in self.plugins.return_plugins():
            if isinstance(x, SmartPlugin):
                plugin_config_name = x.get_configname()
                if x.metadata is not None:
                    functions_infos = list(
                        self.__build_plugin_function_info(x.metadata))
                    if len(functions_infos) > 0:
                        self.plugin_functions[plugin_config_name] = []
                        for function in functions_infos:
                            self.plugin_functions[plugin_config_name].append(
                                function)

    def __assign_default_value_for_parameter_as_shadow(self, input_value, param):
        s_type, field_name = translate_to_blockly_shadow_type(
            param["p_type"], param['p_default'])

        if s_type is not None:
            shadow = input_value.add_shadow(s_type)
            if field_name is not None:
                shadow.add_field(field_name, param['p_default'])

    def __create_root_category(self) -> BlocklyCategory:
        self.__build_plugin_functions_list()
        root_cat = BlocklyCategory(self.__root_name)
        for plugin in self.plugin_functions:
            plugin_category = root_cat.add_category(plugin)
            plugin_category.add_block("shng_function_return_ignorer")
            for function in self.plugin_functions[plugin]:
                new_block = plugin_category.add_block("shng_plugin_function")
                new_block.name = f'{plugin}.{function["m_name"]}'
                new_block.add_field("PO_NAME", plugin)  # which plugin-object
                new_block.add_field(
                    "M_NAME", function["m_name"])  # which method?
                tool_tip_text = ''
                if function["m_description"]:
                    tool_tip_text = function["m_description"].get(
                        self.language, '')
                    if not tool_tip_text:
                        tool_tip_text = function["m_description"].get('en', '')
                new_block.add_field("M_DESC", tool_tip_text)
                new_block.add_field("P_COUNT", len(function["m_pars"]))
                for index, param in enumerate(function["m_pars"], 1):
                    input_value = new_block.add_value(f"PARAM{index}")
                    self.__assign_default_value_for_parameter_as_shadow(
                        input_value, param)
                    new_block.add_field(f"P{index}_NAME", param["p_name"])
                    new_block.add_field(
                        f"P{index}_TYPE_RAW", param["p_type_raw"])
                new_block.add_field("M_RET_TYPE", function["m_ret_type"])
                new_block.add_field(
                    "M_RET_TYPE_RAW", function["m_ret_type_raw"])

        return root_cat

    def get_xml(self, document: Document) -> Element:
        root_cat = self.__create_root_category()
        return root_cat.get_xml(document)

    def get_dict_for_json(self) -> dict:
        root_cat = self.__create_root_category()
        ret_dict = root_cat.get_dict_for_json()
        return ret_dict


class ShngBlockFactory():

    def __init__(self, translation_function):
        self.__items_to_blocks = None
        self.__plugin_functions_to_blocks = None
        self.translate = translation_function

    def __tree_generator(self):
        yield self.__get_blocks_shng_triggers()
        yield self.__get_blocks_shng_tools()
        yield self.__get_blocks_shng_plugin_functions()
        yield self.__get_blocks_shng_write_to_items()
        yield self.__get_blocks_shng_read_from_items()
        yield BlocklySeparator()
        yield self.__get_blocks_if()
        yield self.__get_blocks_boolean()
        yield self.__get_blocks_loops()
        yield self.__get_blocks_math()
        yield self.__get_blocks_text()
        yield self.__get_blocks_lists()
        yield self.__get_blocks_colours()
        yield BlocklyCategory(self.translate("Variables"), "VARIABLE")
        # yield BlocklyCategory(self.translate("Functions"), "PROCEDURE")

    def __get_blocks_shng_triggers(self) -> BlocklyCategory:
        if self.__items_to_blocks is None:
            self.__items_to_blocks = ShngItemsToBlockly()
        root_cat = self.__items_to_blocks.get(self.translate(
            "TB_SHNG_Triggers"), ShngItemsToBlockly.wrap_trigger)
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
            "LOGTEXT").add_shadow("text")
        dew_point = tool_cat.add_block("shtools_dewpoint")
        dew_point.add_value("HUM").add_shadow(
            "math_number").add_field("NUM", "42")
        dew_point.add_value("TEMP").add_shadow(
            "math_number").add_field("NUM", "21")
        tool_cat.add_block("shtools_fetchurl")
        tool_cat.add_block("shtools_fetchurl2")

        root_cat.add_block("sh_logic_main")
        return root_cat

    def __get_blocks_shng_plugin_functions(self) -> ShngPluginFunctionsToBlockly:
        if self.__plugin_functions_to_blocks is None:
            self.__plugin_functions_to_blocks = ShngPluginFunctionsToBlockly(
                self.translate("SmartHomeNG Plugin-Functions"),
                self.translate("LANGUAGE_LOCALE"))
        return self.__plugin_functions_to_blocks

    def __get_blocks_shng_write_to_items(self) -> BlocklyCategory:
        if self.__items_to_blocks is None:
            self.__items_to_blocks = ShngItemsToBlockly()
        return self.__items_to_blocks.get(self.translate("TB_SHNG_Items_To"), ShngItemsToBlockly.wrap_in_setter)

    def __get_blocks_shng_read_from_items(self) -> BlocklyCategory:
        if self.__items_to_blocks is None:
            self.__items_to_blocks = ShngItemsToBlockly()
        root_cat = self.__items_to_blocks.get(self.translate(
            "TB_SHNG_Items_From"), ShngItemsToBlockly.wrap_in_getter)
        root_cat.add_block("shng_logic_trigger_dict")
        return root_cat

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
            "TIMES").add_shadow("math_number").add_field("NUM", "10")
        root_cat.add_block("controls_whileUntil")
        for_b = root_cat.add_block("controls_for")
        for_b.add_field("VAR", "i")
        for_b.add_value("FROM").add_shadow("math_number").add_field("NUM", "1")
        for_b.add_value("TO").add_shadow("math_number").add_field("NUM", "1")
        for_b.add_value("BY").add_shadow("math_number").add_field("NUM", "1")
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
            "DELTA").add_shadow("math_number").add_field("NUM", 1)
        root_cat.add_block("math_round")
        root_cat.add_block("math_on_list")
        root_cat.add_block("math_modulo")
        constr = root_cat.add_block("math_constrain")
        constr.add_value("LOW").add_shadow("math_number").add_field("NUM", 1)
        constr.add_value("HIGH").add_shadow(
            "math_number").add_field("NUM", 100)
        random = root_cat.add_block("math_random_int")
        random.add_value("FROM").add_shadow("math_number").add_field("NUM", 1)
        random.add_value("TO").add_shadow("math_number").add_field("NUM", 100)
        root_cat.add_block("math_random_float")
        return root_cat

    def __get_blocks_text(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Text"))
        root_cat.add_block("text")
        root_cat.add_block("text_join")
        root_cat.add_block("text_append").add_value("TEXT").add_shadow("text")
        root_cat.add_block("text_length")
        root_cat.add_block("text_isEmpty")
        index_of = root_cat.add_block("text_indexOf")
        index_of.add_value("VALUE").add_shadow("text")
        index_of.add_value("FIND").add_shadow("text")
        
        char_at = root_cat.add_block("text_charAt")
        char_at.add_value("VALUE").add_shadow("text").add_field("TEXT", "Durchsuchter Text")
        char_at.add_value("AT").add_shadow("math_number").add_field("NUM", 5)
        substring = root_cat.add_block("text_getSubstring")
        substring.add_value("STRING").add_shadow("text").add_field("TEXT", "Durchsuchter Text")
        substring.add_value("AT1").add_shadow("math_number").add_field("NUM", 1)
        substring.add_value("AT2").add_shadow("math_number").add_field("NUM", 10)
        root_cat.add_block("text_changeCase")
        root_cat.add_block("text_trim")
        return root_cat

    def __get_blocks_lists(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Lists"))
        root_cat.add_block("lists_create_empty")
        root_cat.add_block("lists_create_with")
        root_cat.add_block("lists_repeat").add_value(
            "NUM").add_shadow("math_number").add_field("NUM", 5)
        root_cat.add_block("lists_length")
        root_cat.add_block("lists_isEmpty")
        root_cat.add_block("lists_indexOf").add_value("VALUE").add_shadow(
            "variables_get")
        root_cat.add_block("lists_getIndex").add_value("VALUE").add_shadow(
            "variables_get")
        root_cat.add_block("lists_setIndex").add_value("LIST").add_shadow(
            "variables_get")
        root_cat.add_block("lists_getSublist").add_value("LIST").add_shadow(
            "variables_get")
        return root_cat

    def __get_blocks_colours(self) -> BlocklyCategory:
        root_cat = BlocklyCategory(self.translate("Colours"))
        root_cat.add_block("colour_picker")
        rgb = root_cat.add_block("colour_rgb")
        rgb.add_value("RED").add_shadow("math_number").add_field("NUM", 100)
        rgb.add_value("GREEN").add_shadow("math_number").add_field("NUM", 50)
        rgb.add_value("BLUE").add_shadow("math_number").add_field("NUM", 0)
        blender = root_cat.add_block("colour_blend")
        blender.add_value("COLOUR1").add_shadow(
            "colour_picker").add_field("COLOUR", "#ff0000")
        blender.add_value("COLOUR2").add_shadow(
            "colour_picker").add_field("COLOUR", "#3333ff")
        blender.add_value("RATIO").add_shadow(
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
