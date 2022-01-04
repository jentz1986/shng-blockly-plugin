/**
 * @license
 * Visual Blocks Editor for smarthome.py
 *
 * Copyright 2015 Dirk Wallmeier
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview Variable blocks for Blockly.
 * @author DW
 */
"use strict";

Blockly.Blocks["sh_item_obj"] = {
    init: function () {
        var hiddenFieldPath = new Blockly.FieldTextInput("Path");
        hiddenFieldPath.setVisible(false);
        var hiddenFieldType = new Blockly.FieldTextInput("Type");
        hiddenFieldType.setVisible(false);
        var fixedFieldName = new Blockly.FieldTextInput("Name");
        this.appendDummyInput().appendField(fixedFieldName, "N").appendField(hiddenFieldPath, "P").appendField(hiddenFieldType, "T");
        this.setOutput(true, "shItemType");
        this.setColour(210);
        this.setTooltip(this.getFieldValue("P"));
        this.setHelpUrl("http://www.example.com/"); // TODO: Set proper URL
        this.setEditable(false);
    },
};

Blockly.Python["sh_item_obj"] = function (block) {
    var iPath = block.getFieldValue("P");
    var code = iPath;
    return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks["sh_item_get"] = {
    /**
     * Block for item getter. -> this is a "Sensor"
     * @this Blockly.Block
     */
    init: function () {
        this.setHelpUrl("");
        this.setColour(260);
        this.appendValueInput("ITEMOBJECT").setCheck("shItemType").appendField("Wert von");
        this.setInputsInline(true);
        this.setOutput(true);
        this.setTooltip("Gibt den Wert des Items zurück.");
    },
};

Blockly.Python["sh_item_get"] = function (block) {
    var itemobj = Blockly.Python.valueToCode(block, "ITEMOBJECT", Blockly.Python.ORDER_ATOMIC) || "item";
    var code = 'sh.' + itemobj + "()";
    return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks["sh_item_set"] = {
    /**
     * Block for item setter.
     * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#7wv5ve
     */
    init: function () {
        this.setHelpUrl("http://www.example.com/");
        this.setColour(260);
        this.appendValueInput("ITEMOJECT").setCheck("shItemType").appendField("setze");
        this.appendValueInput("VALUE").appendField("auf den Wert");
        this.setInputsInline(true);
        this.setPreviousStatement(true);
        this.setNextStatement(true);
        this.setTooltip("");
    },
};

Blockly.Python["sh_item_set"] = function (block) {
    var itemobject = Blockly.Python.valueToCode(block, "ITEMOJECT", Blockly.Python.ORDER_ATOMIC) || "item";
    var value = Blockly.Python.valueToCode(block, "VALUE", Blockly.Python.ORDER_ATOMIC) || "0";
    var code = 'sh.' + itemobject + "(" + value + ")\n";
    return code;
};

Blockly.Blocks["sh_item_hasattr"] = {
    init: function () {
        this.appendDummyInput().appendField("das Item");
        this.appendValueInput("ITEM").setCheck("shItemType");
        this.appendDummyInput().appendField("hat das Attribut").appendField(new Blockly.FieldTextInput("default"), "ATTR");
        this.setInputsInline(true);
        this.setOutput(true, "Boolean");
        this.setColour(120);
        this.setTooltip("");
        this.setHelpUrl("http://www.example.com/");
    },
};

Blockly.Python["sh_item_hasattr"] = function (block) {
    var value_item = Blockly.Python.valueToCode(block, "ITEM", Blockly.Python.ORDER_ATOMIC);
    var text_attr = block.getFieldValue("ATTR");
    var code = "sh.iHasAttr(" + value_item + ", " + text_attr + " )";
    return [code, Blockly.Python.ORDER_NONE];
};
