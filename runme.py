from pathlib import Path
from IPython import start_ipython  # type: ignore
from traitlets.config import Config  # type: ignore


config = Config()
shell_config = config.InteractiveShell
shell_config.autoindent = True
shell_config.colors = "Neutral"

environment = Path(__file__).parent.absolute() / "shell.py"
app_config = config.InteractiveShellApp
app_config.exec_lines = [
    "%load_ext autoreload",
    "%autoreload 2",
    f"%run {environment}",
]

start_ipython(config=config)
