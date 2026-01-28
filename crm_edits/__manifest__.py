{
    'name': 'Crm Edits',
    'summary': 'Crm Edits',
    'author': "Ezzeldin Mohamed",
    'version': '19.1',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'sale_crm',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/crm_lead_view.xml',
        'views/sale_order_view.xml',
        # 'data/',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
