# Serialization structures

class SubmitResult:
    # Variables
    error_code = ''
    warnings   = ''
    output     = ''

    def __str__(self):
        return "[Warnings]:\n" + self.warnings + "\n[Code]:\n" + self.error_code + " \n[Output]:\n" + self.output + "\n";

    def __init__(self, warnings, error_code=0, output=''):
        self.warnings  = warnings
        self.error_code= error_code
        self.output    = output

class CodeSubmit:
    # Variables
    file_name      = ''
    file_data      = ''
    prog_language  = ''

    def __init__(self, file_name, file_data, prog_language):
        self.file_name = file_name
        self.file_data = file_data
        self.prog_language = prog_language

