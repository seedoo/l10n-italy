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

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, tools


class MailComposeMessage(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def _get_def_server(self, cr, uid, context=None):
        res = self.pool.get('fetchmail.server').search(
            cr, uid, [('user_ids', 'in', uid), ('pec', '=', True), ('state','=','done')], context=context)
        return res and res[0] or False

    def default_get(self, cr, uid, fields, context=None):
        result = super(MailComposeMessage, self).default_get(cr, uid, fields, context=context)
        if context and context.get('new_pec_mail', False):
            result['subject'] = False
        return result

    _columns = {
        'server_id': fields.many2one('fetchmail.server', 'Server', domain="[('pec', '=', True),('user_ids', 'in', uid),('state','=','done')]"),
    }
    _defaults = {
        'model': 'res.partner',
        'res_id': lambda obj, cr, uid, context: uid,
        'server_id': _get_def_server
    }

    def send_mail(self, cr, uid, ids, context=None):
        """ Override of send_mail to duplicate attachments linked to the
        email.template.
            Indeed, basic mail.compose.message wizard duplicates attachments
            in mass
            mailing mode. But in 'single post' mode, attachments of an
            email template
            also have to be duplicated to avoid changing their ownership. """
        for wizard in self.browse(cr, uid, ids, context=context):
            if context.get('new_pec_mail'):
                context['mail_notify_user_signature'] = False
                context['new_pec_server_id'] = wizard.server_id.id
                for partner in wizard.partner_ids:
                    if not partner.pec_mail:
                        raise osv.except_osv(_('Error'), _('No PEC mail for partner %s') % partner.name)
        return super(MailComposeMessage, self).send_mail(cr, uid, ids, context=context)

    def get_message_data(self, cr, uid, message_id, context=None):
        if not message_id:
            return {}
        if context is None:
            context = {}
        if context.get('reply_pec'):
            result = super(MailComposeMessage, self).get_message_data(
                cr, uid, message_id, context=context)
            # get partner_ids from action context
            partner_ids = context.get('default_partner_ids', [])
            # update the result
            result.update({
                'partner_ids': partner_ids,
            })
            return result
        else:
            return super(MailComposeMessage, self).get_message_data(
                cr, uid, message_id, context=context)

    def _check_server_access(self, cr, uid, context=None):
        if 'new_pec_mail' in context and context['new_pec_mail']:
            user_ids = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)

            if len(user_ids.allowed_server_ids.ids) == 0:
                raise osv.except_osv(_('Warning!'),
                                     _("L'utente %s non e' associato a nessun PEC Server") % user_ids.name)

            disabled_server_name = ""
            all_server_disabled = True
            for server in self.pool.get('fetchmail.server').browse(cr, SUPERUSER_ID, user_ids.allowed_server_ids.ids):
                if server.pec == False:
                    disabled_server_name += server.name + " "
                else:
                    all_server_disabled = False
                    break

            if all_server_disabled:
                raise osv.except_osv(_('Warning!'),
                                     _(
                                         "Nessuno dei server a cui è associato l'utente (%s) è abilitato in modalità PEC Server") % disabled_server_name)

            return True

    def get_record_data(self, cr, uid, values, context=None):
        """ Returns a defaults-like dict with initial values for the
        composition wizard when sending an email related a previous email
        (parent_id) or a document (model, res_id).
        This is based on previously computed default values. """

        self._check_server_access(cr, uid, context)
        if context is None:
            context = {}

        result = super(MailComposeMessage, self).get_record_data(
            cr, uid, values, context=context)
        if 'reply_pec' in context and context['reply_pec']:
            if 'parent_id' in values:
                parent = self.pool.get('mail.message').browse(
                    cr, uid, values.get('parent_id'), context=context)
                result['parent_id'] = parent.id
                subject = parent.subject
                re_prefix = _('Re:')
                if subject and not \
                        (subject.startswith('Re:') or
                         subject.startswith(re_prefix)):
                    subject = "%s %s" % (re_prefix, subject)
                    result['subject'] = subject
        return result