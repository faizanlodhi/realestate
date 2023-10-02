from odoo import models
# from xlsxwriter.format import border


class ReportXlsx(models.AbstractModel):
    _name = 'report.library.excel_wizard_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Excel Report'

    def generate_xlsx_report(self, workbook, data, partners):

        sheet = workbook.add_worksheet('Books')
        bold = workbook.add_format({'bold': True})
        sheet.set_column('D:D',22 )
        sheet.set_column('E:E',22)
        sheet.set_column('F:F',22)
        sheet.set_column('G:G',22)
        sheet.set_column('H:H',22)
        sheet.set_column('I:I',22)
        row =3
        col =3
        sheet.write(row, col, 'Name', bold)
        sheet.write(row, col+1, 'Publisher', bold)
        sheet.write(row, col+2, 'Pages', bold)
        sheet.write(row, col+3, 'Release Date', bold)
        sheet.write(row, col+4, 'State', bold)
        sheet.write(row, col+5, 'Retail Price', bold)


        for books in data['books']:
            row +=1
            sheet.write(row, col, books['name'])
            sheet.write(row, col+1, books['publisher_id'][1])
            sheet.write(row, col+2, books['pages'])
            sheet.write(row, col+3, books['date_release'])
            sheet.write(row, col+4, books['state'])
            sheet.write(row, col+5, books['retail_price'])



