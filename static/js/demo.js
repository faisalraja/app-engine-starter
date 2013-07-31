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

// All Cloud Enpoints Buttons
// refer to config.py comment on how to create one
var CLIENT_ID = client_id,
    SCOPES = 'https://www.googleapis.com/auth/userinfo.email',
    token = null;

$('a.endpoints-btn').click(function(e){
    e.preventDefault();
    var params = {};
    if ($(this).data('params')) {
        params = $(this).data('params');
    }

    var method = $(this).data('method');

    if (method == 'hello') {
        gapi.client.demo.hello({world: 'hi', limit: 5}).execute(function(resp){
            $('#main-container').prepend('<div class="alert alert-success">Response: ' + JSON.stringify(resp) + '</div>');
        });
    } else if (method == 'login') {
        console.log('before authorize');
        gapi.auth.authorize({client_id: CLIENT_ID, scope: SCOPES, immediate: false, response_type: 'token id_token'}, function(){
            var request = gapi.client.oauth2.userinfo.get().execute(function(resp) {
                console.log(resp);
                if (!resp.code) {
                    token = gapi.auth.getToken();
                    token.access_token = token.id_token;
                    gapi.auth.setToken(token);
                    gapi.client.set
                    // User is signed in
                    $('#main-container').prepend('<div class="alert alert-success">Response: Signed In with token ' + token.id_token + '</div>');
                }
            });
        });
    } else if (method == 'get_email') {
        gapi.client.demo.user.email().execute(function(resp){
            $('#main-container').prepend('<div class="alert alert-success">Response: ' + JSON.stringify(resp) + '</div>');
        });
    } else if (method == 'delete_shouts') {
        gapi.client.demo.mappers.deleteShouts().execute(function(resp){
            $('#main-container').prepend('<div class="alert alert-success">Response: ' + JSON.stringify(resp) + '</div>');
        });
    }
});

// Called when gapi client libraries is loaded, can be changed below onload=init
var init = function() {
    // This is called when the google apis client is ready
    var demoApi = '//' + window.location.host + '/_ah/api';
    gapi.client.load('demo', 'v1', function() {
        window.console && console.log('Ready for calls');
    }, demoApi);

    // Oauth
    gapi.client.load('oauth2', 'v2', function() {
        window.console && console.log('Ready for oauth');
        // Check if already logged in
        gapi.auth.authorize({client_id: CLIENT_ID, scope: SCOPES, immediate: true, response_type: 'token id_token'});
    });
};
