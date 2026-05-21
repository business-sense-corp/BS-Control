{
    "name": "BS Control",
    "version": "19.0.1.0.0",
    "summary": "Business Sense Control Management",
    "description": """
        BS Control module for managing business control information.
        This module extends standard Odoo models using inheritance.
    """,
    "category": "Business",
    "author": "Business Sense",
    "depends": [
        "contacts",
        "project",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/project_project_views.xml",
        "views/bs_control_menus.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}