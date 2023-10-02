# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    _description = 'Abstract Archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active


class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']
    # _inherit = 'library.book'
    _description = 'Library Book'

    _order = 'date_release desc, name'

    # date_return = fields.Date('Date to return')
    name = fields.Char('Title', required=True, index=True)
    short_name = fields.Char('Short Title', translate=True, index=True)
    notes = fields.Text('Internal Notes')
    isbn = fields.Char('ISBN')
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('borrowed','Borrowed'),
         ('lost', 'Lost')],
        'State', default="draft")
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated', copy=False)
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)
    old_edition = fields.Many2one('library.book', string='Old Edition')
    manager_remarks = fields.Text('Manager Remarks')

    reader_rating = fields.Float(
        'Reader Average Rating',
        digits=(14, 4),  # Optional precision (total, decimals),
    )
    author_ids = fields.Many2many('res.partner', string='Authors')
    cost_price = fields.Float('Book Cost', digits='Book Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary(
        'Retail Price')  # optional attribute: currency_field='currency_id' incase currency field have another name then 'currency_id'

    publisher_id = fields.Many2one('res.partner', string='Publisher',
                                   # optional:
                                   ondelete='set null',
                                   context={},
                                   domain=[],
                                   )

    publisher_city = fields.Char('Publisher City', related='publisher_id.city', readonly=True)

    category_id = fields.Many2one('library.book.category')
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age', inverse='_inverse_age', search='_search_age',
        store=False,
        compute_sudo=True,
    )

    def grouped_data(self):
        data = self._get_average_cost()
        logger.info("Groupped Data %s" % data)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [('cost_price', "!=", False)],  # Domain
            ['category_id', 'cost_price:avg'],  # Fields to access
            ['category_id']  # group_by
        )
        return grouped_result

    class BookCategory(models.Model):
        _name = 'library.book.category'

        name = fields.Char('Category')
        description = fields.Text('Description')




    student_id = fields.Char(
        name="Student Name"
    )

    def find_book(self):
        domain = [
            '|',
            '&',  ('name', 'ilike', 'Rich Dad Poor'),
            ('category_id.name', 'ilike', 'Novel'),
            '&', ('name', 'ilike', 'The Catcher in the Rye'),
            ('category_id.name', 'ilike', 'Fiction')
             ]
        books = self.search(domain)
        logger.info('Books found: %s', books)
        print(books)
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()






    def log_all_library_members(self):
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Books: %s', filtered_books)
        print(all_books)

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
        return all_books.filtered(predicate)



    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self.ensure_one()
        self.change_state('available')

    def make_borrowed(self):
        self.ensure_one()
        self.change_state('borrowed')

    def make_lost(self):
        self.ensure_one()
        self.change_state('lost')

    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({
            'book_id': self.id,
            'borrower_id': self.env.user.partner_id.id,
        })



    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }

        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        record = self.env['library.book.category'].create(parent_category_val)
        return True




    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    # This reverse method of _compute_age. Used to make age_days field editable
    # It is optional if you don't want to make compute field editable then you can remove this
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    # This used to enable search on copute fields
    # It is optional if you don't want to make enable search then you can remove this
    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    def name_get(self):
        """ This method used to customize display name of the record """
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result
        for book in self:
            authors = book.author_ids.mapped('name')
        name = '%s (%s)' % (book.name, ', '.join(authors))
        result.append((book.id, name))
        return result

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)', 'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        logger.info('Books Authors: %s', books_authors)
        print(books_authors)

    @api.model
    def get_author_names(self, all_books):
        return all_books.mapped('author_ids.name')

    def sort_books(self):
        all_books = self.search([])
        books_sorted = self.sort_books_by_date(all_books)
        logger.info('Books before sorting: %s', all_books)
        logger.info('Books after sorting: %s', books_sorted)
        print(books_sorted)

    @api.model
    def sort_books_by_date(self, all_books):
        return all_books.sorted(key='date_release')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books',
        # relation='library_book_res_partner_rel'  # optional
    )

    count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)




# class BooksRecordXlsx(models.Model):
#     _name = 'library.book.xlsx'
#     # _inherit = 'report.library.book.abstract'
#     def generate_xlsx_report(self, workbook, data, books):
#         print("############################")

class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}

    _description = 'Library Member'

    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')

    @api.model
    def create(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )
            return super(LibraryBook, self).create(values)

    def write(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError('You are not allowed to modify '
                                'manager_remarks'
                                )
            return super(LibraryBook, self).write(values)

    @api.model
    def _name_search(self, name='', args=None,operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            args += ['|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)
                     ]
            return super(LibraryBook, self)._name_search(
                name=name, args=args, operator=operator,
                limit=limit, name_get_uid=name_get_uid)
