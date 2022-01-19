"use strict";

const SHNG_TRIGGER_TYPES = ["sh_trigger_item", "sh_trigger_cycle", "sh_trigger_sun", "sh_trigger_daily", "sh_trigger_init"];

let DO_NOT_GENERATE_CODE_FOR_TRIGGERS = (block_obj) => ""; // because code generation is handled in the sh_logic_main

/**
 * Logic main block
 */
Blockly.Blocks["sh_logic_main"] = {
    init: function () {
        this.setColour(125);
        this.appendDummyInput("LOGIC")
            .setAlign(Blockly.ALIGN_LEFT)
            .appendField("Logik-Name:")
            .appendField(new Blockly.FieldTextInput("new_logic"), "LOGIC_NAME");
        this.appendDummyInput().appendField("Logik aktiv:").appendField(new Blockly.FieldCheckbox("TRUE"), "ACTIVE");
        this.appendDummyInput().appendField("Diese Logik starten,");
        this.appendStatementInput("TRIGGERS").setCheck(SHNG_TRIGGER_TYPES);
        this.appendDummyInput().appendField("Und dann mache folgendes:");
        this.appendStatementInput("DO");
        this.setPreviousStatement(false);
        this.setNextStatement(false);
        this.setDeletable(false);
    },
    getShngLogicName: function () {
        return this.getFieldValue("LOGIC_NAME");
    },
    getShngLogicActive: function () {
        return this.getFieldValue("ACTIVE") == "TRUE" ? "True" : "False";
    },
    getShngTriggers: function (predicate) {
        var children = this.getChildren();
        var to_return = [];
        if (null != children && children.length > 0) {
            var child = children[0];
            do {
                if (predicate(child)) {
                    to_return.push(child);
                }
                child = child.getNextBlock();
            } while (child != null);
            return to_return;
        }
        return null;
    },
    getShngCycleTriggerDefinition: function () {
        var ccscs = this.getShngTriggers((child) => child.isShngTriggerDefinition && child.type == "sh_trigger_cycle");
        if (ccscs != null && ccscs.length > 0) {
            return ccscs[0].getShngTriggerInformation(); // Only the first trigger is relevant
        }
    },
    getShngItemTriggerDefinitions: function () {
        var ccscs = this.getShngTriggers((child) => child.isShngTriggerDefinition && child.type == "sh_trigger_item");
        if (ccscs != null && ccscs.length > 0) {
            return ccscs;
        }
    },
    getShngCrontabTriggerDefinitions: function () {
        var ccscs = this.getShngTriggers((child) => child.isShngTriggerForCrontab);
        if (ccscs != null && ccscs.length > 0) {
            return ccscs;
        }
    },
    getShngYamlDeclaration: function () {
        let indent = "    ";
        let commentAfter = 60;

        let to_return = [];
        to_return.push(this.getShngLogicName() + ":");
        {
            let fileNameLine = indent + "filename: blockly_" + this.getShngLogicName() + ".py";
            let comment = this.getCommentText();
            if (comment) {
                fileNameLine = fileNameLine.padEnd(commentAfter);
                fileNameLine += "# " + comment;
            }
            to_return.push(fileNameLine);
        }
        var cycle_trigger = this.getShngCycleTriggerDefinition();
        if (cycle_trigger) {
            let cycle_def = indent + "cycle: " + cycle_trigger.cycle;
            if (cycle_trigger.trigger_value) {
                cycle_def += " = " + cycle_trigger.trigger_value;
            }
            if (cycle_trigger.comment) {
                cycle_def = cycle_def.padEnd(commentAfter) + "# " + cycle_trigger.comment;
            }
            to_return.push(cycle_def);
        }
        var item_triggers = this.getShngItemTriggerDefinitions();
        if (item_triggers) {
            to_return.push(indent + "watch_item:");
            item_triggers.forEach((item) => {
                let info = item.getShngTriggerInformation();
                let line = indent + "  - " + info.watch_item;
                if (info.trigger_value) {
                    line += " = " + info.trigger_value;
                }
                if (info.comment) {
                    line = line.padEnd(commentAfter) + "# " + info.comment;
                }
                to_return.push(line);
            });
        }
        var crontab_triggers = this.getShngCrontabTriggerDefinitions();
        if (crontab_triggers) {
            to_return.push(indent + "crontab:");
            crontab_triggers.forEach((item) => {
                let info = item.getShngTriggerInformation();
                let line = indent + "  - " + item.getShngTriggerCrontab();
                if (info.trigger_value) {
                    line += " = " + info.trigger_value;
                }
                if (info.comment) {
                    line = line.padEnd(commentAfter) + "# " + info.comment;
                }
                to_return.push(line);
            });
        }
        return to_return.join("\n");
    },
    getInterpreterDeclaration: function () {
        var to_return = [];
        var logicname = this.getShngLogicName();
        {
            let active = this.getShngLogicActive();
            let comment = this.getCommentText();
            if (!comment) {
                comment = " ";
            }
            to_return.push("#comment#" + logicname + "#active: " + active + "#" + comment);
        }
        var cycle_trigger = this.getShngCycleTriggerDefinition();
        if (cycle_trigger) {
            let cycle_def = "#trigger#" + logicname + "#cycle: " + cycle_trigger.cycle;
            if (cycle_trigger.trigger_value) {
                cycle_def += " = " + cycle_trigger.trigger_value;
            }
            cycle_def += "# ";
            if (cycle_trigger.comment) {
                cycle_def += cycle_trigger.comment;
            }
            to_return.push(cycle_def);
        }
        var crontab_triggers = this.getShngCrontabTriggerDefinitions();
        if (crontab_triggers) {
            let crontabList = [];
            let commentList = [];
            crontab_triggers.forEach((item) => {
                let info = item.getShngTriggerInformation();
                let crontabAndValue = "'" + item.getShngTriggerCrontab();
                if (info.trigger_value) {
                    crontabAndValue += " = " + info.trigger_value;
                }
                crontabAndValue += "'";
                let comment = info.comment ? "'" + info.comment + "'" : "''";
                crontabList.push(crontabAndValue);
                commentList.push(comment);
            });
            to_return.push("#trigger#" + logicname + "#crontab: [" + crontabList.join(",") + "]#[" + commentList.join(",") + "]");
        }
        var item_triggers = this.getShngItemTriggerDefinitions();
        if (item_triggers) {
            let watchItemList = [];
            let commentList = [];
            item_triggers.forEach((item) => {
                let info = item.getShngTriggerInformation();
                let watch_item = "'" + info.watch_item + "'";
                let comment = info.comment ? "'" + info.comment + "'" : "''";
                watchItemList.push(watch_item);
                commentList.push(comment);
            });
            to_return.push("#trigger#" + logicname + "#watch_item: [" + watchItemList.join(",") + "]#[" + commentList.join(",") + "]");
        }
        return to_return.join("\n");
    },
};

Blockly.Python["sh_logic_main"] = function (block) {
    var code = block.getInterpreterDeclaration() + "\n\n";

    code += '"""\n' + "Logic " + this.getShngLogicName() + "\n";
    code += "THIS FILE WAS GENERATED FROM A BLOCKLY LOGIC WORKSHEET - DON'T EDIT THIS FILE, use the Blockly plugin instead !\n";
    let commentText = this.getCommentText();
    if (commentText) {
        code += "\n" + commentText + "\n";
    }

    code += "\nto be configured in /etc/logic.yaml:\n";
    code += block.getShngYamlDeclaration();
    code += '\n"""\n\n';

    code += "logic_active = " + this.getShngLogicActive() + "\n";
    code += "if (logic_active == True):\n";

    var logic_body_python_code = Blockly.Python.statementToCode(block, "DO");
    code += logic_body_python_code;
    return code + "\n\n";
};

Blockly.Blocks["shng_logic_trigger_dict"] = {
    init: function () {
        this.setColour(190);
        var dictFieldDropdown = new Blockly.FieldDropdown([
            ["Triggerwert", "value"],
            ["Auslöser", "by"],
            ["Pfad des auslösenden Items", "source"],
            ["Weitere Details des Auslösers", "source_details"],
            ["Triggerziel", "dest"],
        ]);
        this.appendDummyInput().appendField(dictFieldDropdown, "DICTFIELD").appendField("aus der Auslösung dieser Logik");
        this.setInputsInline(true);
        this.setOutput(true);
        this.setPreviousStatement(false);
        this.setNextStatement(false);
        this.setTooltip("");
    },
};

Blockly.Python["shng_logic_trigger_dict"] = function (block) {
    let code = 'trigger["' + block.getFieldValue("DICTFIELD") + '"]';
    return [code, Blockly.Python.ORDER_NONE];
};

/**
 * Trigger die Logic bei Änderung des Items
 */
Blockly.Python["sh_trigger_item"] = DO_NOT_GENERATE_CODE_FOR_TRIGGERS;
Blockly.Blocks["sh_trigger_item"] = {
    init: function () {
        this.isShngTriggerDefinition = true;
        this.setColour(190);
        this.appendDummyInput().appendField("wenn sich");
        this.appendValueInput("TRIG_ITEM").setCheck("shItemType").setAlign(Blockly.ALIGN_LEFT);
        this.appendDummyInput().appendField("ändert");
        this.setInputsInline(true);
        this.setPreviousStatement(true, SHNG_TRIGGER_TYPES);
        this.setNextStatement(true, SHNG_TRIGGER_TYPES);
        this.setTooltip(
            "Der Logikinhalt wird ausgeführt, wenn sich der Wert des Items ändert. Dann wird der neue Wert des Items als Triggerwert an die Logik übergeben."
        );
    },
    isShngTriggerForCrontab: false,
    isShngTriggerDefinition: true,
    getShngTriggerInformation: function () {
        var itemcode = Blockly.Python.valueToCode(this, "TRIG_ITEM", Blockly.Python.ORDER_ATOMIC);
        var comment = this.getCommentText();

        return {
            type: "trigger_item",
            watch_item: itemcode,
            comment: comment,
        };
    },
};

/**
 * Trigger ... alle x sec.
 */
Blockly.Python["sh_trigger_cycle"] = DO_NOT_GENERATE_CODE_FOR_TRIGGERS;
Blockly.Blocks["sh_trigger_cycle"] = {
    /**
     * Block for
     * @this Blockly.Block
     */
    init: function () {
        this.setColour(190);
        let numberOfSecondsField = new Blockly.FieldNumber(60, 0);
        numberOfSecondsField.setValidator(Blockly.FieldTextInput.nonnegativeIntegerValidator);
        this.appendDummyInput()
            .appendField("in einem Zyklus von")
            .appendField(numberOfSecondsField, "TRIG_CYCLE")
            .appendField("Sekunden,")
            .appendField("mit dem Triggerwert:")
            .appendField(new Blockly.FieldTextInput("trigger_id"), "NAME");
        this.setInputsInline(false);
        this.setPreviousStatement(true, SHNG_TRIGGER_TYPES);
        this.setNextStatement(true, SHNG_TRIGGER_TYPES);
        this.setTooltip("Block wird nach vorgegebener Zeit wiederholt ausgeführt.");
    },
    isShngTriggerForCrontab: false,
    isShngTriggerDefinition: true,
    getShngTriggerInformation: function () {
        var trigger_id = this.getFieldValue("NAME");
        var comment = this.getCommentText();
        var cycle = this.getFieldValue("TRIG_CYCLE");

        return {
            type: "trigger_cycle",
            trigger_value: trigger_id,
            cycle: cycle,
            comment: comment,
        };
    },
};

/**
 * Trigger vor/nach Sonnen-Auf-/Untergang.
 */
Blockly.Python["sh_trigger_sun"] = DO_NOT_GENERATE_CODE_FOR_TRIGGERS;
Blockly.Blocks["sh_trigger_sun"] = {
    /**
     * Block for
     * @this Blockly.Block
     */
    init: function () {
        this.setColour(190);
        let offsetField = new Blockly.FieldNumber(0, 0);
        offsetField.setValidator(Blockly.FieldTextInput.nonnegativeIntegerValidator);
        this.appendDummyInput()
            .appendField(offsetField, "OFFSET")
            .appendField("Minuten")
            .appendField(
                new Blockly.FieldDropdown([
                    ["vor", "-"],
                    ["nach", "+"],
                ]),
                "PLUSMINUS"
            )
            .appendField("Sonnen-")
            .appendField(
                new Blockly.FieldDropdown([
                    ["Aufgang", "sunrise"],
                    ["Untergang", "sunset"],
                ]),
                "SUN"
            )
            .appendField(", mit dem Triggerwert")
            .appendField(new Blockly.FieldTextInput("trigger_id"), "NAME");
        this.setInputsInline(false);
        this.setPreviousStatement(true, SHNG_TRIGGER_TYPES);
        this.setNextStatement(true, SHNG_TRIGGER_TYPES);
        this.setTooltip("Block wird vor/nach Sonnenaufgang/Sonnenuntergang ausgeführt.");
    },
    isShngTriggerForCrontab: true,
    isShngTriggerDefinition: true,
    getShngTriggerInformation: function () {
        var trigger_id = this.getFieldValue("NAME");
        var comment = this.getCommentText();
        var cronstring = this.getShngTriggerCrontab();

        return {
            type: "trigger_sun",
            trigger_value: trigger_id,
            crontab: cronstring,
            comment: comment,
        };
    },
    getShngTriggerCrontab: function () {
        var offset = this.getFieldValue("OFFSET");
        var plusminus = this.getFieldValue("PLUSMINUS");
        var sun = this.getFieldValue("SUN");
        return "" + sun + plusminus + offset;
    },
};

/**
 * Trigger taeglich um HH:MM Uhr
 */
Blockly.Python["sh_trigger_daily"] = DO_NOT_GENERATE_CODE_FOR_TRIGGERS;
Blockly.Blocks["sh_trigger_daily"] = {
    init: function () {
        this.setColour(190);
        this.appendDummyInput()
            .appendField("jeden Tag um")
            .appendField(new Blockly.FieldNumber(0, 0), "HH")
            .appendField(":")
            .appendField(new Blockly.FieldNumber(0, 0), "MM")
            .appendField("Uhr, mit dem Triggerwert")
            .appendField(new Blockly.FieldTextInput("trigger_id"), "NAME");
        this.setInputsInline(false);
        this.setPreviousStatement(true, SHNG_TRIGGER_TYPES);
        this.setNextStatement(true, SHNG_TRIGGER_TYPES);
        this.setTooltip("Block wird täglich zur gegebenen Stunde ausgeführt.");
    },
    isShngTriggerForCrontab: true,
    isShngTriggerDefinition: true,
    getShngTriggerInformation: function () {
        var trigger_id = this.getFieldValue("NAME");
        var comment = this.getCommentText();
        var cronstring = this.getShngTriggerCrontab();
        return {
            type: "trigger_daily",
            trigger_value: trigger_id,
            crontab: cronstring,
            comment: comment,
        };
    },
    getShngTriggerCrontab: function () {
        var hh = this.getFieldValue("HH");
        var mm = this.getFieldValue("MM");
        return "" + mm + " " + hh + " * *";
    },
};

/**
 * Trigger bei Initialisierung auslösen
 */
Blockly.Python["sh_trigger_init"] = DO_NOT_GENERATE_CODE_FOR_TRIGGERS;
Blockly.Blocks["sh_trigger_init"] = {
    init: function () {
        this.setColour(190);
        this.appendDummyInput()
            .appendField("bei jeder Initialisierung von SmarthomeNG,")
            .appendField("mit dem Triggerwert")
            .appendField(new Blockly.FieldTextInput("Init"), "NAME");
        this.setInputsInline(false);
        this.setPreviousStatement(true, SHNG_TRIGGER_TYPES);
        this.setNextStatement(true, SHNG_TRIGGER_TYPES);
        this.setTooltip("Block wird bei der Initialisierung ausgeführt.");
    },
    isShngTriggerForCrontab: true,
    isShngTriggerDefinition: true,
    getShngTriggerInformation: function () {
        var trigger_id = this.getFieldValue("NAME");
        var comment = this.getCommentText();
        var cronstring = this.getShngTriggerCrontab();

        return {
            type: "trigger_init",
            trigger_value: trigger_id,
            crontab: cronstring,
            comment: comment,
        };
    },
    getShngTriggerCrontab: function () {
        return "init";
    },
};
