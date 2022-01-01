from xml.dom import minidom


class ShngItemsToBlockly():

    def __init__(self, sh_items_api):
        self.sh_items_api = sh_items_api
        self.xml_document_root = minidom.Document()

    def __remove_prefix(self, string, prefix):
        """
        Remove prefix from a string

        :param string: String to remove the profix from
        :param prefix: Prefix to remove from string
        :type string: str
        :type prefix: str

        :return: Strting with prefix removed
        :rtype: str
        """
        if string.startswith(prefix):
            return string[len(prefix):]
        return string

    def __create_node(self, tag, text=None, attributes_dict={}):
        root_tag = self.xml_document_root.createElement(tag)
        if text:
            textNode = self.xml_document_root.createTextNode(text)
            root_tag.appendChild(textNode)
        for key in attributes_dict:
            root_tag.setAttribute(key, attributes_dict[key])

        return root_tag

    def __create_root_category(self):
        root_items = filter(lambda i: i._path.find('.') == -1 and i._path not in ['env_daily', 'env_init', 'env_loc', 'env_stat'],
                            sorted(self.sh_items_api.return_items(),
                                   key=lambda k: str.lower(k['_path']), reverse=False))
        root = self.__iterate_items(root_items, "SmartHomeNG Items")
        root.appendChild(self.__create_node(
            "block", "-", {"type": "sh_item_get"}))  # Blockly has issues with empty tags (<tag /> doesn't work, but <tag></tag>!)
        root.appendChild(self.__create_node(
            "block", "-", {"type": "sh_item_set"}))
        root.appendChild(self.__create_node(
            "block", "-", {"type": "sh_item_hasattr"}))

        return root

    def __create_item_block(self, item, name):
        block = self.__create_node("block", attributes_dict={
            "type": "sh_item_obj", "name": item._path})
        block.appendChild(self.__create_node(
            "field", name, {"name": "N"}))
        block.appendChild(self.__create_node(
            "field", item._path, {"name": "P"}))
        block.appendChild(self.__create_node(
            "field", item.type(), {"name": "T"}))

        return block

    def __iterate_items(self, items, name, prefix_to_cut=""):
        category = self.__create_node(
            "category", attributes_dict={"name": name})

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
                        if child_category.firstChild:
                            child_category.insertBefore(
                                this_item, child_category.firstChild)
                        else:
                            child_category.appendChild(this_item)
                    if child_category.firstChild:
                        count_of_child_blocks = sum(1 for _ in filter(
                            lambda n: n.tagName == "block", child_category.childNodes))
                    else:
                        count_of_child_blocks = 0
                    child_category.setAttribute(
                        "name", f"{shortname} ({count_of_child_blocks})")
                    category.appendChild(child_category)
            else:
                if (item.type() != 'foo') or (item() != None):
                    category.appendChild(
                        self.__create_item_block(item, shortname))

        if not category.firstChild:
            return None

        return category

    def get_xml_string(self):
        return self.__create_root_category().toprettyxml(indent="    ")
