{
    "name": "Dellyman Package Integration (POC)",
    "version": "18.0.1.0.0",
    "summary": "POC: scan tracking ID, fetch from Dellyman API",
    "description": "Minimal POC to scan tracking IDs and fetch package data from Dellyman API.",
    "category": "Warehouse",
    "author": "ChatGPT",
    "depends": ["base"],
    "data": [
        "views/scan_tracking_wizard_view.xml",
        "views/menu.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False,
    "auto_install": False
}
