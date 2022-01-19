var ShngBlockly_Toolbox = { kind: "categoryToolbox", contents: [] };

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

ShngBlockly_Engine.calledWhenWorkspaceWasUpdated = function (event) {
    ShngBlockly_Engine.validateWorkspace();
    ShngBlockly_Engine.refreshPython();
    $("h6")
        .first()
        .html("<b>Logic: </b>" + ShngBlockly_Engine.getLogicName() + "<br />" + ShngBlockly_Engine.validationSummary);
};

ShngBlockly_Engine.init = function (blockly_area_id, python_area_id) {
    ShngBlockly_Engine.blockly_workspace = Blockly.inject(blockly_area_id, {
        grid: { spacing: 25, length: 3, colour: "#ccc", snap: true },
        media: "static/blockly/media/",
        maxInstances: { sh_logic_main: 1, sh_trigger_cycle: 1, sh_trigger_init: 1 },
        toolbox: ShngBlockly_Toolbox,
        move: { wheel: true },
        zoom: { controls: true, maxScale: 2, minScale: 0.5 },
    });

    ShngBlockly_Engine.blockly_workspace.addChangeListener(ShngBlockly_Engine.calledWhenWorkspaceWasUpdated);

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

ShngBlockly_Engine.validationSummary = "";

ShngBlockly_Engine.validationIssueList = [];

ShngBlockly_Engine.validateWorkspace = function () {
    ShngBlockly_Engine.validationIssueList = [];

    var topBlocks = ShngBlockly_Engine.blockly_workspace.getTopBlocks();
    var allBlocksWithinLogicOrFunction = true;
    topBlocks.forEach((block) => {
        if (block.type == "sh_logic_main" || block.type == "procedures_defreturn" || block.type == "procedures_defnoreturn") {
            // These types may be root-elements
        } else {
            allBlocksWithinLogicOrFunction = false;
        }
    });
    if (!allBlocksWithinLogicOrFunction) {
        ShngBlockly_Engine.validationIssueList.push("Alle Elemente müssen entweder Teil der Logik, oder einer Funktion sein.");
    }

    if (ShngBlockly_Engine.validationIssueList.length == 0) {
        ShngBlockly_Engine.validationSummary = "Keine Syntaxfehler!";
    } else {
        if (ShngBlockly_Engine.validationIssueList.length == 1) {
            ShngBlockly_Engine.validationSummary = ShngBlockly_Engine.validationIssueList[0];
        } else {
            ShngBlockly_Engine.validationSummary = "" + ShngBlockly_Engine.validationIssueList.length + " Probleme";
        }
    }
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

ShngBlockly_Engine.getLogicName = function () {
    var logicname = null;
    var topblocks = ShngBlockly_Engine.blockly_workspace.getTopBlocks();
    topblocks.forEach((topblock) => {
        if (topblock.data == "sh_logic_main") {
            logicname = topblock.getFieldValue("LOGIC_NAME");
        }
    });
    return logicname;
};

/**
 * Save XML and PYTHON code to file on SmartHomeNG server.
 */
ShngBlockly_Engine.saveBlocks = function () {
    var pycode = Blockly.Python.workspaceToCode(ShngBlockly_Engine.blockly_workspace);
    var xmldom = Blockly.Xml.workspaceToDom(ShngBlockly_Engine.blockly_workspace);
    var xmltxt = Blockly.Xml.domToText(xmldom);
    var logicname = ShngBlockly_Engine.getLogicName();

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
        ShngBlockly_UI.showDialog(ShngBlockly_Constants.DialogMessageUnsavedChanges, ShngBlockly_Constants.DialogMessageAreYouSure, onOK, onCancel);
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
        ShngBlockly_UI.showLoadLogicDialog();
    });
};

ShngBlockly_UI.performUpdateBlocks = function (logicName) {
    ShngBlockly_Engine.loadBlocks(logicName);
    $("#genericModal").modal("hide");
};

ShngBlockly_UI.showDialog = function (content, caption = "", onOK = null, onCancel = null) {
    if (onOK != null) {
        wrappedOnOK = function () {
            onOK();
            $("#genericModal").modal("hide");
        };
        $("#genericModal .modal-footer button.OK").unbind().click(wrappedOnOK);
        $("#genericModal .modal-header button.close").unbind().click(wrappedOnOK);
        $("#genericModal .modal-footer button.OK").show();
    } else {
        $("#genericModal .modal-footer button.OK").hide();
    }
    if (onCancel != null) {
        wrappedOnCncl = function () {
            onCancel();
            $("#genericModal").modal("hide");
        };
        $("#genericModal .modal-footer button.Cancel").unbind().click(wrappedOnCncl);
        $("#genericModal .modal-header button.close").unbind().click(wrappedOnCncl);
        $("#genericModal .modal-footer button.Cancel").show();
    } else {
        $("#genericModal .modal-footer button.Cancel").hide();
    }
    $("#genericModal .modal-header h4").html(caption);
    $("#genericModal .modal-body div").html(content);

    $("#genericModal").modal("show");
};

ShngBlockly_UI.dialogOK = function (message) {
    ShngBlockly_UI.showDialog(message, "Info", function () {}); // TODO: Übersetzen
};

ShngBlockly_UI.dialogErrorOK = function (message) {
    ShngBlockly_UI.showDialog(message, "ERROR", function () {}); // TODO: Übersetzen
};

ShngBlockly_UI.showLoadLogicDialog = function () {
    ShngBlockly_UI.showDialog('<div id="logicList"></div>', ShngBlockly_Constants.DialogMessageLoadLogicHead, null, function () {});
    $.ajax({
        url: ShngBlockly_Constants.ApiEndpointGetLogics,
        type: "GET",
        async: false,
        data: { uniq_param: new Date().getTime() },
        success: function (response) {
            $("#logicList").empty();
            response.logics.forEach((logic) => {
                $("#logicList").append(
                    "<button onclick=\"ShngBlockly_UI.performUpdateBlocks('" + logic + '\')" class="btn btn-shng btn-sm">' + logic + "</button>"
                );
            });
        },
    });
};

$(document).ready(function () {
    ShngBlockly_Engine.init("content_blocks", "content_python");
    /**
     * TODO: Read Parameter from UI to identify logic to be loaded
     */
    ShngBlockly_Engine.loadBlocks();

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

    $("body").append(
        '<div class="modal" id="genericModal"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h4 class="modal-title"></h4><button type="button" class="close">&times;</button></div><div class="modal-body"><div></div></div><div class="modal-footer"><button type="button" class="btn OK">' +
            ShngBlockly_Constants.OKText +
            '</button><button type="button" class="btn btn-danger Cancel">' +
            ShngBlockly_Constants.CancelText +
            "</button></div></div></div></div>"
    );
});

ShngBlockly_Engine.loadToolbox();
