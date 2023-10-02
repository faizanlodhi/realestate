from odoo import models, fields, api


class PrintBooksWizard(models.TransientModel):
    _name = 'print.books.wizard'
    _description = 'Print Books'
    # name = fields.Char('Title', required=True, index=True)
    date_from = fields.Date("From Date")
    date_to = fields.Date("To Date")

    def print_report(self):
        data ={
            'date_from' : self.date_from,
            'date_to' : self.date_to

            }
        return self.env.ref('library.report_library_book_wizard').report_action(self, data=data)

    # def print_excel_report(self):
    #     print("Excel report")
    #     data={
    #         'date_from': self.date_from,
    #         'date_to': self.date_to
    #     }
    #     return self.env.ref('library.excel_report').report_action(self, data=data)

    def print_xls_report(self):
        domain = []
        date_from = self.date_from
        date_to = self.date_to
        if date_from:
            domain+=[('date_release', '>=', date_from)]
        if date_to:
            domain+=[('date_release', '<=', date_to)]

        books = self.env['library.book'].search_read(domain)
        # book = self.env['res.users'].browse(data.get('name'))
        data = {'books': books,
                'form_data': self.read()[0]}
        # print(docs)
        # print(data)
        return self.env.ref('library.excel_wizard_report').report_action(self, data=data)

class ReportPDF(models.AbstractModel):
    _name = 'report.library.books_details'
    _description = 'Wizard Book'


    def _get_report_values(self, docids, data=None):
        domain = [('state', '!=', 'cancel')]
        if data.get('date_from'):
            domain.append(('date_release', '>=', data.get('date_from')))
        if data.get('date_to'):
            domain.append(('date_release', '<=', data.get('date_to')))

        docs = self.env['library.book'].search(domain)
        book = self.env['res.users'].browse(data.get('name'))
        data.update({'book':book.name})
        # print(docs)
        # print(data)
        return {
            'docs_model':"library.book",
            'docs':docs,
            'datas': data
        }

