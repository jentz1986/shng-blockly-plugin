class ShngItemsToBlockly():

    def __init__(self, sh_items_api):
        self.sh_items_api = sh_items_api


    def get_hierarchy_as_xml_string(self):
        mytree = self.__build_tree()
        return mytree + "<sep>-</sep>\n"


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


    def __build_tree(self):
        # Get top level items
        toplevelitems = []
        allitems = sorted(self.sh_items_api.return_items(), key=lambda k: str.lower(k['_path']), reverse=False)
        for item in allitems:
            if item._path.find('.') == -1:
                if item._path not in ['env_daily', 'env_init', 'env_loc', 'env_stat']:
                    toplevelitems.append(item)

        xml = '\n'
        for item in toplevelitems:
            xml += self.__build_treelevel(item)
#        self.logger.info("log_tree #  xml -> '{}'".format(str(xml)))
        return xml
                

    def __build_treelevel(self, item, parent='', level=0):
        """
        Builds one tree level of the items
        
        This methods calls itself recursively while there are further child items
        """
        childitems = sorted(item.return_children(), key=lambda k: str.lower(k['_path']), reverse=False)

        name = self.__remove_prefix(item._path, parent+'.')
        if childitems != []:
            xml = ''
            if (item.type() != 'foo') or (item() != None):
#                self.logger.info("item._path = '{}', item.type() = '{}', item() = '{}', childitems = '{}'".format(item._path, item.type(), str(item()), childitems))
                xml += self.__build_leaf(name, item, level+1)
                xml += ''.ljust(3*(level)) + '<category name="{0} ({1})">\n'.format(name, len(childitems)+1)
            else:
                xml += ''.ljust(3*(level)) + '<category name="{0} ({1})">\n'.format(name, len(childitems))
            for grandchild in childitems:
                xml += self.__build_treelevel(grandchild, item._path, level+1)

            xml += ''.ljust(3*(level)) + '</category>  # name={}\n'.format(item._path)
        else:
            xml = self.__build_leaf(name, item, level)
        return xml


    def __build_leaf(self, name, item, level=0):
        """
        Builds the leaf information for an entry in the item tree
        """
#        n = item._path.title().replace('.','_')
        n = item._path
        xml = ''.ljust(3*(level)) + '<block type="sh_item_obj" name="' + name + '">\n'
        xml += ''.ljust(3*(level+1)) + '<field name="N">' + n + '</field>>\n'
        xml += ''.ljust(3*(level+1)) + '<field name="P">' + item._path + '</field>>\n'
        xml += ''.ljust(3*(level+1)) + '<field name="T">' + item.type() + '</field>>\n'
        xml += ''.ljust(3*(level)) + '</block>\n'
        return xml
        
