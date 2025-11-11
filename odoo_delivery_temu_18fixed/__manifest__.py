{
    "name": "Delivery Intake - TEMU (Odoo 18 Fixed)",
    "version": "18.0.1.2.0",
    "summary": "Scan TEMU packages, batch them and assign warehouse locations",
    "category": "Warehouse/Delivery",
    "depends": ["base", "stock", "barcodes"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/delivery_batch_views.xml",
        "views/delivery_package_views.xml",
        "views/scan_wizard_views.xml"
    ],
    "installable": True,
    "application": False
}
