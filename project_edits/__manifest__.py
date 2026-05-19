{
    'name': 'Project Edits',
    'summary': 'Project Edits',
    'author': "Ezzeldin Mohamed",
    'version': '19.1',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'project',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/project_project_view.xml',
        'views/res_partner_view.xml',
        'views/project_task_view.xml',
        # 'data/',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
