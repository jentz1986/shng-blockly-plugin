var ShngBlockly_Engine = {};
ShngBlockly_Engine.blockly_workspace = null;
ShngBlockly_Engine.python_editor = null;

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

//ShngBlockly_Engine.python_editor.setSize($('#codemirror_frame').width(), $('#codemirror_frame').height());

ShngBlockly_Engine.refreshPython = function () {
    var pycode = Blockly.Python.workspaceToCode(ShngBlockly_Engine.blockly_workspace);
    ShngBlockly_Engine.python_editor.setValue(pycode);
};

ShngBlockly_Engine.init = function (blockly_area_id, python_area_id) {
    var toolboxtxt = document.getElementById("toolbox").outerHTML;
    var toolboxXml = Blockly.Xml.textToDom(toolboxtxt);

    ShngBlockly_Engine.blockly_workspace = Blockly.inject(blockly_area_id, {
        grid: { spacing: 25, length: 3, colour: "#ccc", snap: true },
        media: "static/blockly/media/",
        toolbox: toolboxXml,
        zoom: { controls: true, wheel: true },
    });

    // Blockly.svgResize(ShngBlockly_Engine.workspace);

    ShngBlockly_Engine.python_editor = CodeMirror.fromTextArea(document.getElementById(python_area_id), {
        mode: { name: "python" },
        lineNumbers: true,
        readOnly: true,
        lineWrapping: true,
        viewportMargin: Infinity,
        extraKeys: {
            "Ctrl-Q": function (cm) {
                cm.foldCode(cm.getCursor());
            },
        },
        foldGutter: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
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
        Blockly.Xml.domToWorkspace(xml, ShngBlockly_Engine.blockly_workspace);
        ShngBlockly_Engine.refreshPython();
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
    var topblock = ShngBlockly_Engine.blockly_workspace.getTopBlocks()[0];
    if (topblock.data == "sh_logic_main") {
        logicname = ShngBlockly_Engine.blockly_workspace.getTopBlocks()[0].getFieldValue("LOGIC_NAME");
    }
    //ShngBlockly_Engine.workspace;
    var pycode = Blockly.Python.workspaceToCode(ShngBlockly_Engine.blockly_workspace);
    var xmldom = Blockly.Xml.workspaceToDom(ShngBlockly_Engine.blockly_workspace);
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
    var count = ShngBlockly_Engine.blockly_workspace.getAllBlocks().length;
    if (count < 2 || window.confirm(Blockly.Msg.DELETE_ALL_BLOCKS.replace("%1", count))) {
        ShngBlockly_Engine.blockly_workspace.clear();
    }
    ShngBlockly_Engine.refreshPython();
};

$(document).ready(function () {
    $('.nav-tabs a').on('shown.bs.tab', function(event){
        var x = $(event.target).text();
        if (x.includes("Python")) {
            ShngBlockly_Engine.refreshPython();
        }        
    });

    ShngBlockly_Engine.init("content_blocks", "content_python");
    ShngBlockly_Engine.loadBlocks();
});
