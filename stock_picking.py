from openerp import models, fields, api, _

class StockPicking(models.Model):
    _inherit= 'stock.picking'


    def _compute_embarque(self):
        cp = self.env['carta.porte.line']
        res = cp.search([['remision_id', '=', self.id]])

        if len(res) > 1:
            self.embarque1_id = res[0].name
            self.embarque2_id = res[1].name
        elif len(res) == 1:
            self.embarque1_id = res[0].name

    embarque1_id = fields.Many2one('carta.porte', 'Orden de embarque', compute='_compute_embarque')
    embarque2_id = fields.Many2one('carta.porte', 'Segundo embarque', compute='_compute_embarque')
