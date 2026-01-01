import pkgutil
import google.adk
import importlib

def find_class(package, name):
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(modname)
            if hasattr(module, name):
                print(f"FOUND {name} in {modname}")
                return
        except ImportError:
            pass
        except Exception:
            pass

print("Searching for ContextCacheConfig in google.adk...")
find_class(google.adk, "ContextCacheConfig")
