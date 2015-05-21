$(function () {
    // Global vars, for easy debugging in console.
    window.jqconsole = $('#console').jqconsole('', '>>> ');
    console.log = function (data) {
        jqconsole.Write(data + "\n", 'jqconsole-output');
    }
    // Display a helpful message and twiddle thumbs as it loads.
    console.log('Init PyPy.js, it\'s big, so this might take a while...\n')

    window.vm = new PyPyJS();

    // Send all VM output to the console.
    vm.stdout = vm.stderr = function (data) {
        jqconsole.Write(data, 'jqconsole-output');
    }

    vm.ready.then(function () {
        // jqconsole.Reset();

        // Print version information
        vm.eval('import sys').then(function () {
            vm.eval('print("Python v" + sys.version)')
        });

        // Create an 'InteractiveConsole' to simulate the python shell.
        vm.eval('import code').then(function () {
            vm.eval('c = code.InteractiveConsole()').then(function () {
                // Prompt for input, send it to the console, rinse, repeat.
                window.doPrompt = function () {
                    jqconsole.Prompt(true, function (input) {
                        var code = input.replace(/\\/g, '\\\\').replace(/'/g, '\\\'');
                        code = 'r = c.push(\'' + code + '\')';
                        vm.eval(code).then(function () {
                            return vm.get('r').then(function (r) {
                                // r==1 means that it's a multi-line definition,
                                // so change the prompt accordingly.
                                if (r) {
                                    jqconsole.SetPromptLabel('... ');
                                } else {
                                    jqconsole.SetPromptLabel('>>> ');
                                }
                                setTimeout(doPrompt, 0);
                            });
                        });
                    });
                };
                doPrompt();
            });
        });
    });
});
