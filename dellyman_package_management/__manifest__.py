{
    'name': 'Dellyman Package Management',
    'version': '1.0',
    'summary': 'Manage packages, batches, and locations for Dellyman workflow',
    'description': """
        Custom package, location, and batch management workflow.
    """,
    'author': 'Your Company',
    'category': 'Operations',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/package_batch_views.xml',
        'views/package_order_views.xml',
        'views/package_location_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}