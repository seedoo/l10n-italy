# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014-2015 Agile Business Group http://www.agilebg.com
#    @authors
#       Alessio Gerace <alessio.gerace@gmail.com>
#       Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#       Roberto Onnis <roberto.onnis@innoviu.com>
#
#   About license see __openerp__.py
#
##############################################################################

from openerp import models, fields


class FetchmailServer(models.Model):

    _inherit = "fetchmail.server"

    pec = fields.Boolean(
        "Account PEC",
        help="Check if this server is PEC")

    pec_account_alias = fields.Many2one(
            'mail.alias', 'Alias account PEC', domain=[('alias_name', '!=', False)])

    user_ids = fields.Many2many(
        'res.users',
        'fetchmail_server_user_rel', 'server_id', 'user_id',
        string='Users allowed to use this server')

    out_server_id = fields.One2many(
        'ir.mail_server',
        'in_server_id',
        string='Outgoing Server',
        readonly=True,
        copy=False)

    force_create_partner_from_mail = fields.Boolean(
        "Force Create Partner",
        help="If checked then if there is no partner"
             " to link a fetched mail with,"
             "the system creates a contact partner")

    associate_pec_by_other_alias = fields.Boolean("Associa le PEC tramite altri alias", default=False)

    def get_fetch_server_pec(self, cr, uid, context=None):
        server_ids = self.search(cr, uid, [('user_ids', '=', uid)])
        return server_ids