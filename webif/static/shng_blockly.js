var ShngBlockly_Toolbox = { kind: "categoryToolbox", contents: [] }

var ShngBlockly_Engine = {};

ShngBlockly_Engine.blockly_workspace = null;

ShngBlockly_Engine.python_editor = null;

ShngBlockly_Engine.refreshPython = function () {
    var pycode = Blockly.Python.workspaceToCode(ShngBlockly_Engine.blockly_workspace);
    ShngBlockly_Engine.python_editor.setValue(pycode);
};

ShngBlockly_Engine.workspaceShouldBeSaved = function () {
    undoStack = ShngBlockly_Engine.blockly_workspace.getUndoStack();
    return undoStack.length > 0;
};

ShngBlockly_Engine.init = function (blockly_area_id, python_area_id) {
    ShngBlockly_Engine.blockly_workspace = Blockly.inject(blockly_area_id, {
        grid: { spacing: 25, length: 3, colour: "#ccc", snap: true },
        media: "static/blockly/media/",
        // TODO: maxInstances: { "shng_logic_main": 1},
        toolbox: ShngBlockly_Toolbox,
        zoom: { controls: true, wheel: true },
    });

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

ShngBlockly_Engine.loadToolbox = function () {
    var request = $.ajax({
        url: ShngBlockly_Constants.ApiEndpointLoadToolbox,
    });
    request.done(function (response) {
        ShngBlockly_Toolbox = response;
        ShngBlockly_Engine.blockly_workspace.updateToolbox(ShngBlockly_Toolbox);
    });
    request.fail(function (jqXHR, txtStat) {
        ShngBlockly_UI.dialogErrorOK(ShngBlockly_Constants.DialogMessageCannotLoad + " Toolbox");
    });
};

/**
 * Restore code blocks from file on SmartHomeNG server
 */
ShngBlockly_Engine.loadBlocks = function (logicName = null) {
    if (logicName == null) {
        logicName = ShngBlockly_Constants.DefaultLogicTemplate;
    }
    var request = $.ajax({
        url: ShngBlockly_Constants.ApiEndpointLoadLogic,
        data: { logic_name: logicName, uniq_param: new Date().getTime() },
        dataType: "text",
    });
    // we get the XML representation of all the blockly logics from the backend
    request.done(function (response) {
        var xml = Blockly.Xml.textToDom(response);
        ShngBlockly_Engine.blockly_workspace.clear();
        Blockly.Xml.domToWorkspace(xml, ShngBlockly_Engine.blockly_workspace);
        ShngBlockly_Engine.refreshPython();
        ShngBlockly_Engine.blockly_workspace.clearUndo();
    });
    request.fail(function (jqXHR, txtStat) {
        ShngBlockly_UI.dialogErrorOK(ShngBlockly_Constants.DialogMessageCannotLoad + logicName);
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
        url: ShngBlockly_Constants.ApiEndpointSaveLogic,
        type: "POST",
        async: false,
        data: { xml: xmltxt, py: pycode, name: logicname },
        success: function (response) {
            ShngBlockly_Engine.blockly_workspace.clearUndo();
            ShngBlockly_UI.dialogOK(ShngBlockly_Constants.DialogMessageSuccessfullySaved);
        },
    });
};

ShngBlockly_UI = {};

ShngBlockly_UI.checkUnsavedChangesBefore = function (onOK) {
    if (ShngBlockly_Engine.workspaceShouldBeSaved()) {
        onCancel = function () {};
        ShngBlockly_UI.dialogOKCancel(ShngBlockly_Constants.DialogMessageUnsavedChanges, onOK, onCancel);
        return;
    } else {
        onOK();
    }
};

ShngBlockly_UI.actionNew = function () {
    ShngBlockly_UI.checkUnsavedChangesBefore(function () {
        ShngBlockly_Engine.loadBlocks();
    });
};

ShngBlockly_UI.actionSave = function () {
    ShngBlockly_Engine.saveBlocks();
};

ShngBlockly_UI.actionLoad = function () {
    ShngBlockly_UI.checkUnsavedChangesBefore(function () {
        $("#loadLogicDialog").modal("show");
    });
};

ShngBlockly_UI.performUpdateBlocks = function (logicName) {
    ShngBlockly_Engine.loadBlocks(logicName);
    $("#loadLogicDialog").modal("hide");
};

ShngBlockly_UI.dialogOK = function (message) {
    $("#dialogOK .modal-header h4").html("Info"); // TODO: Übersetzen
    $("#dialogOK .modal-body div").html(message);
    $("#dialogOK").modal("show");
};

ShngBlockly_UI.dialogErrorOK = function (message) {
    $("#dialogOK .modal-header h4").html("Error"); // TODO: Übersetzen
    $("#dialogOK .modal-body div").html(message);
    $("#dialogOK").modal("show");
};

ShngBlockly_UI.dialogOKCancel = function (message, onOK, onCancel) {
    wrappedOnOK = function () {
        onOK();
        $("#dialogOKCancel").modal("hide");
    };
    wrappedOnCncl = function () {
        onCancel();
        $("#dialogOKCancel").modal("hide");
    };
    $("#dialogOKCancel .modal-header h4").html("Error"); // TODO: Übersetzen
    $("#dialogOKCancel .modal-header button.close").unbind().click(wrappedOnCncl);
    $("#dialogOKCancel .modal-body div").html(message);
    $("#dialogOKCancel .modal-footer button.OK").unbind().click(wrappedOnOK);
    $("#dialogOKCancel .modal-footer button.Cancel").unbind().click(wrappedOnCncl);
    $("#dialogOKCancel").modal("show");
};

ShngBlockly_UI.renderContentIntoLoadLogicDialog = function (logicList) {
    $("#logicList").empty();
    logicList.forEach((logic) => {
        $("#logicList").append(
            "<button onclick=\"ShngBlockly_UI.performUpdateBlocks('" + logic + '\')" class="btn btn-shng btn-sm">' + logic + "</button>"
        );
    });
};

ShngBlockly_UI.init = function () {
    window.addEventListener("beforeunload", function (e) {
        if (ShngBlockly_Engine.workspaceShouldBeSaved()) {
            e["returnValue"] = ShngBlockly_Constants.DialogMessageUnsavedChanges;
        } else {
            // the absence of a returnValue property on the event will guarantee the browser unload happens
            delete e["returnValue"];
        }
    });

    $(".nav-tabs a").on("shown.bs.tab", function (event) {
        var x = $(event.target).text();
        if (x.includes(ShngBlockly_Constants.TabHeaderPythonEditor)) {
            ShngBlockly_Engine.refreshPython();
        }
    });

    $("#loadLogicDialog").on("show.bs.modal", function () {
        $.ajax({
            url: ShngBlockly_Constants.ApiEndpointGetLogics,
            type: "GET",
            async: false,
            data: { uniq_param: new Date().getTime() },
            success: function (response) {
                ShngBlockly_UI.renderContentIntoLoadLogicDialog(response.logics);
            },
        });
    });
};

$(document).ready(function () {
    ShngBlockly_Engine.init("content_blocks", "content_python");
    ShngBlockly_UI.init();

    /**
     * TODO: Read Parameter from UI to identify logic to be loaded
     */
    ShngBlockly_Engine.loadBlocks();
});

ShngBlockly_Engine.loadToolbox();