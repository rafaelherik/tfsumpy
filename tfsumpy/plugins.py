import importlib.util
import glob
import os

def load_plugins(context, plugin_dir="plugins"):
    """Load and register plugins from the specified directory."""
    if not os.path.isdir(plugin_dir):
        return
    for path in glob.glob(os.path.join(plugin_dir, "*.py")):
        spec = importlib.util.spec_from_file_location("plugin", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "register"):
            mod.register(context) 