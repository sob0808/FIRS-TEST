/** Simple barcode scan helper: listens for an input field event and posts to controller. Adapt to your scanner hardware. */
odoo.define('dellyman.scan', function(require){
    'use strict';
    var ajax = require('web.ajax');
    // this is intentionally minimal. Integrate with your barcode input in the UI.
    window.dellymanScan = function(tracking, batch_id){
        return ajax.post('/dellyman/scan', {tracking: tracking, batch_id: batch_id});
    };
});
