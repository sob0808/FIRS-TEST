odoo.define('dellyman.scan', function(require){
    'use strict';
    var ajax = require('web.ajax');
    window.dellymanScan = function(tracking, batch_id){
        return ajax.jsonRpc('/dellyman/scan', 'call', {tracking: tracking, batch_id: batch_id});
    };
});
