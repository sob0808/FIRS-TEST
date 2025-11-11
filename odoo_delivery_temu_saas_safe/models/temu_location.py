from odoo import models, fields

class TemuLocation(models.Model):
    _name = 'temu.location'
    _description = 'TEMU Internal Location'

    name = fields.Char(string='Location Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    note = fields.Text(string='Notes')
