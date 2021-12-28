/**
TODO: Import Prettify / PrettyPrint for Python Output
*/

var ShngBlockly_Engine = {};

/**
 * Blockly's main workspace.
 * @type {Blockly.WorkspaceSvg}
 */
ShngBlockly_Engine.workspace = null;

ShngBlockly_Engine.sleep = function (ms) {
    // TODO: REMOVE
    var start = new Date().getTime();
    var end = start;
    while (end < start + ms) {
        end = new Date().getTime();
    }
};

ShngBlockly_Engine.stop = function () {
    alert("closeEditor called blockly_close_editor on the server, but did nothing else");
    $.ajax({ url: "blockly_close_editor", type: "POST", data: { content: "" } });
    ShngBlockly_Engine.sleep(1000);
    // window.close();
    alert("Magic!");
};

ShngBlockly_Engine.init = function (node_id) {
    var toolboxtxt = document.getElementById("toolbox").outerHTML;
    var toolboxXml = Blockly.Xml.textToDom(toolboxtxt);

    ShngBlockly_Engine.workspace = Blockly.inject(node_id, {
        grid: { spacing: 25, length: 3, colour: "#ccc", snap: true },
        media: "static/blockly/media/",
        toolbox: toolboxXml,
        zoom: { controls: true, wheel: true },
    });
};

/**
 * Restore code blocks from file on SmartHomeNG server
 */
ShngBlockly_Engine.loadBlocks = function () {
    var request = $.ajax({
        url: "blockly_load_logic",
        data: { uniq_param: new Date().getTime() },
        dataType: "text",
    });
    // we get the XML representation of all the blockly logics from the backend
    request.done(function (response) {
        var xml = Blockly.Xml.textToDom(response);
        Blockly.Xml.domToWorkspace(xml, ShngBlockly_Engine.workspace);
        Code.renderContent();
    });
    request.fail(function (jqXHR, txtStat) {
        alert("LoadBlocks - Request failed: " + txtStat);
    });
};

/**
 * Save XML and PYTHON code to file on SmartHomeNG server.
 */
ShngBlockly_Engine.saveBlocks = function () {
    var logicname = "";
    var topblock = ShngBlockly_Engine.workspace.getTopBlocks()[0];
    if (topblock.data == "sh_logic_main") {
        logicname = ShngBlockly_Engine.workspace.getTopBlocks()[0].getFieldValue("LOGIC_NAME");
    }
    //ShngBlockly_Engine.workspace;
    var pycode = Blockly.Python.workspaceToCode(ShngBlockly_Engine.workspace);
    var xmldom = Blockly.Xml.workspaceToDom(ShngBlockly_Engine.workspace);
    var xmltxt = Blockly.Xml.domToText(xmldom);

    $.ajax({
        url: "blockly_save_logic",
        type: "POST",
        async: false,
        data: { xml: xmltxt, py: pycode, name: logicname },
        success: function (response) {
            alert("" + response + " ?");
        },
    });
};

/**
 * Discard all blocks from the workspace.
 */
ShngBlockly_Engine.discardBlocks = function () {
    var count = ShngBlockly_Engine.workspace.getAllBlocks().length;
    if (count < 2 || window.confirm(Blockly.Msg.DELETE_ALL_BLOCKS.replace("%1", count))) {
        ShngBlockly_Engine.workspace.clear();
    }
};
