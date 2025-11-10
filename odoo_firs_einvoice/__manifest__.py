# -*- coding: utf-8 -*-
{
    "name": "FIRS e-Invoice Integration",
    "version": "1.1.2",
    "summary": "Automatic connection to FIRS e-Invoicing (TaxPro Max)",
    "category": "Accounting",
    "author": "Your Company",
    "depends": ["account"],
    "data": [
        "views/firs_config_views.xml",
        "views/account_move_inherit_views.xml",
        "report/invoice_report_templates.xml",
        "data/ir_cron.xml",
        "data/ir_actions_server.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
