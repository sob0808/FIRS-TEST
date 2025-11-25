{
    "name": "Delivery Intake - TEMU (SaaS-safe)",
    "version": "18.0.3.0.0",
    "summary": "Scan TEMU packages, batch them and assign internal locations (SaaS-safe)",
    "description": "Odoo 18 compatible module for scanning and batching TEMU packages. Uses an internal location model to avoid requiring the stock app.",
    "category": "Warehouse/Delivery",
    "depends": ["base", "barcodes"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/scan_wizard_views.xml",
        "views/delivery_batch_views.xml",
        "views/delivery_package_views.xml",
        "views/temu_location_views.xml",
    ],
    "installable": True,
    "application": False,
}
