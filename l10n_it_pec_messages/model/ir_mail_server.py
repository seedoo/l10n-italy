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


class IrMailServer(models.Model):

    _inherit = "ir.mail_server"

    in_server_id = fields.Many2one(
        'fetchmail.server',
        string='Incoming PEC server',
        domain="[('pec', '=', True)]")

    pec = fields.Boolean(
        "Pec Server",
        help="Check if this server is PEC")

    _sql_constraints = [
        ('incomingserver_name_unique', 'unique(in_server_id)',
         'Incoming Server already in use'),
        ]

    def get_mail_server_pec(self, cr, uid, fetch_server_id, context=None):
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(cr, uid,
                                                 [('in_server_id',
                                                   '=',
                                                   fetch_server_id["server_id"])]
                                                 )
        return mail_server_ids

