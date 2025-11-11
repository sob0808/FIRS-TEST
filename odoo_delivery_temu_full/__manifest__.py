{
    "name": "Delivery Intake - TEMU",
    "version": "18.0.1.0.0",
    "summary": "Scan TEMU packages, batch them and assign warehouse locations",
    "description": "Scan, batch, and assign TEMU packages to stock locations.",
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
