{
    "name": "Dellyman Package Management (Clean)",
    "version": "1.0.0",
    "summary": "Manage Dellyman package batches, packages and locations (clean build)",
    "author": "ChatGPT",
    "category": "Operations",
    "depends": ["base","mail"],
    "data": [
        "data/sequence_data.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/package_batch_views.xml",
        "views/package_location_views.xml",
        "views/package_order_views.xml"
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3"
}
