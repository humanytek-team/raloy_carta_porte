from openerp import models, fields, api, _

class StockPicking(models.Model):
    _inherit= 'stock.picking'

    @api.multi
    def _compute_embarque(self):
        #print '_compute_embarque'
        cp = self.env['carta.porte.line']
        for rec in self:
            res = cp.search([['remision_id', '=', rec.id]])

            if len(res) > 1:
                rec.embarque1_id = res[0].carta_id
                rec.embarque2_id = res[1].carta_id
            elif len(res) == 1:
                rec.embarque1_id = res[0].carta_id

    embarque1_id = fields.Many2one('carta.porte', 'Orden de embarque', compute='_compute_embarque')
    embarque2_id = fields.Many2one('carta.porte', 'Segundo embarque', compute='_compute_embarque')

    partner_city = fields.Char('Ciudad',related='partner_id.city', store=True)
    partner_zip = fields.Char('Zip',related='partner_id.zip', store=True)
    partner_state = fields.Char('Estado del pais',related='partner_id.state_id.name', store=True)
    partner_street2 = fields.Char('Colonia',related='partner_id.street2', store=True)
