import re

# Usunięcie ANSI escape kodów
ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')

# Tee jak w Linux'ie
# Przekierowanie outputu do konsoli i pliku, wraz z usunięciem escape kodów ANSI
class Tee:
    def __init__(self, console, log_file):
        self.console = console
        self.log_file = log_file

    def write(self, data):
        # ZAPIS DO KONSOLI (wraz z kodami escape ANSI)
        self.console.write(data)
        self.console.flush()

        # ZAPIS DO PLIKU (bez kod'ów escape ANSI)
        clean_data = ansi_escape.sub('', data)
        self.log_file.write(clean_data)
        self.log_file.flush()

    def flush(self):
        self.console.flush()
        self.log_file.flush()