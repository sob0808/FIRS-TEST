{
    'name': 'Dellyman Package Management',
    'version': '1.0',
    'summary': 'Manage Dellyman package batches, packages and locations',
    'description': 'Custom package, location, and batch management workflow.',
    'author': 'Your Company',
    'category': 'Operations',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/menu.xml',
        'views/package_order_views.xml',
        'views/package_location_views.xml',
        'views/package_batch_views.xml'
    ],
    'installable': True,
    'application': True,
}
