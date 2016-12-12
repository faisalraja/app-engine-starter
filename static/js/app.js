/**
 * This is just to get you started, just remove demo.js from base.html
 * User: faisal
 */

// All JsonRpc Buttons
$('a.rpc-btn').click(function(e){
    e.preventDefault();
    var params = {};
    if ($(this).data('params')) {
        params = $(this).data('params');
    }
    var request = JSON.stringify({'method': $(this).data('method'), 'id': 1, 'jsonrpc': '2.0', 'params': params });
    $('#main-container').prepend('<div class="alert alert-info">Request: ' + request + '</div>');
    $.post(rpcEndpoint, request, function(response) {
        $('#main-container').prepend('<div class="alert alert-success">Response: ' + JSON.stringify(response) + '</div>');
    }, "json");
});

$('a.batch-btn').click(function(e){
    e.preventDefault();
    var batch = [
        {"jsonrpc": '2.0', "method": 'hello', "params": ["world", 2], "id": 5},  // normal request
        {"jsonrpc": '2.0', "method": 'hello'},  // as notification
        {"jsonrpc": '2.0', "method": 'login', "id": 10},
        {"jsonrpc": '2.0', "method": 'no_method', "id": 50} // an error
    ];
    var request = JSON.stringify(batch);
    $('#main-container').prepend('<div class="alert alert-info">Request: ' + request + '</div>');
    $.post(rpcEndpoint, request, function(response) {
        $('#main-container').prepend('<div class="alert alert-success">Response: ' + JSON.stringify(response) + '</div>');
    }, "json");
});

$(function() {

    console.log('TEST');

});