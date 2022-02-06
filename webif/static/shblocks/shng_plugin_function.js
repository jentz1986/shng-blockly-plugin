"use strict";

const SHNG_DATA_TYPES = [
    ["disabled", "void"],
    ["any", "foo"],
    ["bool", "Boolean"],
    ["Array", "Array"],
    ["num", "Number"],
    ["str", "String"],
    ["shItemType", "shItemType"],
];

const SHNG_MAX_PARAM_NUM = 12;

Blockly.Blocks["shng_plugin_function"] = {
    init: function () {
        var parameter_count_input_disabler = function (newValue) {
            let sb = this.getSourceBlock();
            for (let param_no = newValue + 1; param_no <= SHNG_MAX_PARAM_NUM; param_no++) {
                let inp = sb.getInput("PARAM" + param_no);
                inp.setVisible(false);
            }
        };

        var p_count_field = new Blockly.FieldNumber(0, 0, 12);
        p_count_field.setValidator(parameter_count_input_disabler);

        var void_return_type_output_disabler = function (newValue) {
            let sb = this.getSourceBlock();
            if (newValue == "void") {
                sb.setOutput(false);
                sb.setPreviousStatement(true, null);
                sb.setNextStatement(true, null);
            } else {
                sb.setOutput(true, newValue);
                sb.setPreviousStatement(false, null);
                sb.setNextStatement(false, null);
            }
        };
        var output_return_type_field = new Blockly.FieldDropdown(SHNG_DATA_TYPES);
        output_return_type_field.setValidator(void_return_type_output_disabler);

        var tool_tip_setter = function (newValue) {
            let sb = this.getSourceBlock();
            sb.setTooltip(newValue);
        };
        var m_description_field = new Blockly.FieldLabelSerializable("description");
        m_description_field.setValidator(tool_tip_setter);

        this.appendDummyInput()
            .appendField(new Blockly.FieldLabelSerializable("object-name"), "PO_NAME")
            .appendField(".")
            .appendField(new Blockly.FieldLabelSerializable("method-name"), "M_NAME")
            .appendField(":")
            .appendField(new Blockly.FieldLabelSerializable("method-name"), "M_RET_TYPE_RAW");
        this.appendDummyInput()
            .appendField(m_description_field, "M_DESC")
            .appendField(p_count_field, "P_COUNT")
            .appendField(output_return_type_field, "M_RET_TYPE")
            .setVisible(false);
        for (let param_no = 1; param_no <= SHNG_MAX_PARAM_NUM; param_no++) {
            let input_type_assigner = function (newValue) {
                let sb = this.getSourceBlock();
                let inp = sb.getInput("PARAM" + param_no);
                if (newValue != "void") {
                    inp.setCheck(newValue);
                }
            };
            let input_type_field = new Blockly.FieldDropdown(SHNG_DATA_TYPES);
            input_type_field.setValidator(input_type_assigner);
            this.appendValueInput("PARAM" + param_no)
                .appendField(new Blockly.FieldLabelSerializable("p-name"), "P" + param_no + "_NAME")
                .appendField(new Blockly.FieldLabelSerializable("p-type"), "P" + param_no + "_TYPE_RAW");
        }
        this.setInputsInline(false);

        this.setOutput(true);
        this.setPreviousStatement(true);
        this.setNextStatement(true);

        this.setColour(0);
        this.setTooltip("");
        this.setHelpUrl("");
    },
};

Blockly.Python["shng_plugin_function"] = function (block) {
    var pCount = block.getFieldValue("P_COUNT");
    var code = "sh." + block.getFieldValue("PO_NAME") + "." + block.getFieldValue("M_NAME") + "(";
    let param_code = "";
    for (let param_no = 1; param_no <= pCount; param_no++) {
        if (param_code != "") {
            param_code += ", ";
        }
        param_code += Blockly.Python.valueToCode(block, "PARAM" + param_no, Blockly.Python.ORDER_NONE);
    }
    code += param_code + ")";
    if (block.getFieldValue("M_RET_TYPE") == "void") {
        return code;
    } else {
        return [code, Blockly.Python.ORDER_ATOMIC];
    }
};

Blockly.Blocks["shng_function_return_ignorer"] = {
    init: function () {
        this.appendValueInput("EXECUTED").setCheck(null).appendField("Führe Funktion aus").appendField("und ignoriere das Ergebnis");
        this.setInputsInline(false);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
        this.setTooltip("");
        this.setHelpUrl("");
    },
};

Blockly.Python["shng_function_return_ignorer"] = function (block) {
    return Blockly.Python.valueToCode(block, "EXECUTED", Blockly.Python.ORDER_NONE) + "\n";
}