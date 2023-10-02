# -*- coding: utf-8 -*-
{
    'name': "My Library",  # Module title
    'summary': "Manage books easily",  # Module subtitle phrase
    'description': """
            Manage Library
            ==============
    Description related to library.
    """,  # Supports reStructuredText(RST) format
    'author': "Faizan Lodhi",
    'website': "http://www.example.com",
    'category': 'Tools',
    'sequence': '-100',
    'version': '14.0.1',
    'depends': ['base',
                'report_xlsx'],

    'data': [


        'security/groups.xml',
        'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/wizardpdf.xml',
        'reports/excel_wizard_report.xml',
        'reports/excel_report.xml',
        'wizard/print_books_view.xml',
        'views/library_book.xml',
        'views/library_book_categ.xml'

    ],
    # This demo data files will be loaded if db initialize with demo data (commented becaues file is not added in this example)
    # 'demo':
    # ['demo.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
