import importlib
# import submodules sequentially to avoid circular import issues on SaaS
for module in [
    "delivery_batch",
    "delivery_package",
    "temu_location",
]:
    importlib.import_module(f".{module}", __name__)
