"use strict";

let ShngPrimitiveTypesToBlocklyValueTypes = {
    str: "String",
    num: "Number",
    list: "Array",
};

Blockly.Blocks["shng_item_get"] = {
    init: function () {
        this.setHelpUrl("");
        this.setColour(260);

        var prop_chooser_updater = function (newValue) {
            let sb = this.getSourceBlock();
            if (newValue.endsWith("value")) {
                let itemType = sb.getFieldValue("ITEMTYPE");
                sb.setOutput(true, ShngPrimitiveTypesToBlocklyValueTypes[itemType]);
                sb.setFieldValue(ShngPrimitiveTypesToBlocklyValueTypes[itemType], "OUTTYPE");
            } else if (newValue.endsWith("_age")) {
                sb.setOutput(true, "Number");
                sb.setFieldValue("Number", "OUTTYPE");
            } else if (newValue.endsWith("_change") || newValue.endsWith("_update")) {
                sb.setOutput(true, "DateTime");
                sb.setFieldValue("DateTime", "OUTTYPE");
            } else if (newValue.endsWith("_by") || newValue == "type" || newValue == "name" || newValue == "path") {
                sb.setOutput(true, "String");
                sb.setFieldValue("String", "OUTTYPE");
            } else if (newValue == "attributes") {
                sb.setOutput(true, "Array");
                sb.setFieldValue("Array", "OUTTYPE");
            } else if (newValue == "enforce_updates") {
                sb.setOutput(true, "Boolean");
                sb.setFieldValue("Boolean", "OUTTYPE");
            } else {
                sb.setOutput(true);
                sb.setFieldValue("Any", "OUTTYPE");
            }
        };
        var property_dropdown = new Blockly.FieldDropdown([
            ["Wert von", "value"],
            ["Vorheriger Wert von", "last_value"],
            ["Vor-Vorheriger Wert von", "prev_value"],
            ["Ob Änderungen erzwungen werden bei", "enforce_updates"],
            ["Zeitpunkt der letzten Änderung", "last_change"],
            ["Alter der letzten Änderung", "last_change_age"],
            ["Letzter Änderer von", "last_change_by"],
            ["Zeitpunkt der letzten Aktualisierung von", "last_update"],
            ["Alter der letzten Aktualisierung von", "last_update_age"],
            ["Letzter Aktualisierer von", "last_update_by"],
            ["Zeitpunkt der vorherigen Änderung", "prev_change"],
            ["Alter der vorherigen Änderung", "prev_change_age"],
            ["Änderer", "prev_change_by"],
            ["Zeitpunkt der vorherigen Aktualisierung", "prev_update"],
            ["Alter der vorherigen Aktualisierung", "prev_update_age"],
            ["Vorheriger Aktualisierer von", "prev_update_by"],
            ["Typ von", "type"],
            ["Attributliste von", "attributes"],
            ["Name von", "name"],
            ["Pfad von", "path"],
        ]);
        property_dropdown.setValidator(prop_chooser_updater);

        this.appendDummyInput().appendField(property_dropdown, "PROP");
        this.appendValueInput("ITEMOBJECT").setCheck("shItemType");
        this.appendDummyInput().appendField(new Blockly.FieldLabelSerializable(), "ITEMTYPE").setVisible(false);
        this.appendDummyInput().appendField(new Blockly.FieldLabelSerializable(), "OUTTYPE");
        this.setInputsInline(true);
        this.setOutput(true);
        this.setTooltip("Gibt den Wert des Items zurück.");
    },
};

Blockly.Python["shng_item_get"] = function (block) {
    var itemobj = Blockly.Python.valueToCode(block, "ITEMOBJECT", Blockly.Python.ORDER_ATOMIC) || "item";
    var code = "sh." + itemobj + "." + block.getFieldValue("PROP");
    return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks["shng_item_set"] = {
    tooltips: {
        value: "Setzt den Wert des Items auf den angegebenen Wert",
        name: "Setzt den Namen des Items auf den angegebenen Wert",
        enforce_updates: "Setzt die Einstellung ob jede Aktualisierung des Items als Änderung zu betrachten ist",
    },
    init: function () {
        this.setColour(260);
        var prop_chooser_updater = function (newValue) {
            let sb = this.getSourceBlock();
            let inputVALUE = sb.getInput("VALUE");
            sb.setTooltip(sb.tooltips[newValue]);
            inputVALUE.setCheck(null);
            if (newValue == "value") {
                let itemType = sb.getFieldValue("ITEMTYPE");
                switch (ShngPrimitiveTypesToBlocklyValueTypes[itemType]) {
                    case "String":
                        inputVALUE.setShadowDom(Blockly.Xml.textToDom('<shadow type="text">-</shadow>'));
                        inputVALUE.setCheck("String");
                        break;
                    case "Boolean":
                        inputVALUE.setShadowDom(Blockly.Xml.textToDom('<shadow type="logic_boolean">-</shadow>'));
                        inputVALUE.setCheck("Boolean");
                        break;
                    case "Number":
                        inputVALUE.setShadowDom(Blockly.Xml.textToDom('<shadow type="math_number">-</shadow>'));
                        inputVALUE.setCheck("Number");
                        break;
                    default:
                        inputVALUE.setShadowDom(null);
                        break;
                }
            } else if (newValue == "name") {
                sb.setTooltip(sb.tooltips["name"]);
                inputVALUE.setShadowDom(Blockly.Xml.textToDom('<shadow type="text">-</shadow>'));
                inputVALUE.setCheck("String");
            } else if (newValue == "enforce_updates") {
                sb.setTooltip(sb.tooltips["enforce_updates"]);
                inputVALUE.setShadowDom(Blockly.Xml.textToDom('<shadow type="logic_boolean">-</shadow>'));
                inputVALUE.setCheck("Boolean");
            } else {
                inputVALUE.setShadowDom(null);
            }
        };
        var property_dropdown = new Blockly.FieldDropdown([
            ["Wert von", "value"],
            ["Ob Änderungen erzwungen werden bei", "enforce_updates"],
            ["Name von", "name"],
        ]);
        property_dropdown.setValidator(prop_chooser_updater);
        this.appendDummyInput().appendField("Setze").appendField(property_dropdown, "PROP");
        this.appendValueInput("ITEMOBJECT").setCheck("shItemType");
        this.appendValueInput("VALUE").appendField("auf");
        this.appendDummyInput().appendField(new Blockly.FieldLabelSerializable(), "ITEMTYPE").setVisible(false);
        this.appendDummyInput().appendField(new Blockly.FieldLabelSerializable(), "INTYPE");
        this.setInputsInline(true);
        this.setPreviousStatement(true);
        this.setNextStatement(true);
        this.setHelpUrl("http://www.example.com/"); // TODO: Change!
        this.setTooltip(this.tooltips["value"]);
    },
};

Blockly.Python["shng_item_set"] = function (block) {
    var itemobj = Blockly.Python.valueToCode(block, "ITEMOBJECT", Blockly.Python.ORDER_ATOMIC) || "item";
    var value = Blockly.Python.valueToCode(block, "VALUE", Blockly.Python.ORDER_ATOMIC) || "0";
    let prop = block.getFieldValue("PROP");
    if (prop == "value") {
        return "sh." + itemobj + "(" + value + ")";
    }
    return "sh." + itemobj + "." + prop + " = " + value;
};
