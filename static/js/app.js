
function rpcRequest (method, params, callback) {
    var request = JSON.stringify({'method': method, 'id': 1, 'jsonrpc': '2.0', 'params': params});

    $.post('/rpc', request, function(response) {
        callback(response);
    }, "json");
}

$(function() {

    // Form Serializer
    $.fn.serializeObject = function()
    {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    // Match Validator
    $.validator.addMethod('regex', function(value, element, regexp) {
        var re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    }, '');

    // validator
    $.validator.setDefaults({
        highlight: function(element) {
            $(element).closest('.form-group').addClass('has-error');
        },
        unhighlight: function(element) {
            $(element).closest('.form-group').removeClass('has-error');
        },
        errorElement: 'span',
        errorClass: 'help-block',
        errorPlacement: function(error, element) {
            if(element.parent('.input-group').length) {
                error.insertAfter(element.parent());
            } else {
                error.insertAfter(element);
            }
        }
    });

    $.validator.addClassRules({
        required: {
            required: true
        },
        email: {
            email: true
        }
    });

    $('form.validate').validate({
        submitHandler: function (form) {
            try {
                form = $(form);

                var submitBtn = form.find('button[type=submit]'),
                    enableSubmit = function () {
                        if (submitBtn.length) {
                            submitBtn.prop('disabled', false);
                            submitBtn.find('.glyphicon-refresh.spinning').addClass('hide');
                        }
                    };

                if (submitBtn.length) {
                    submitBtn.prop('disabled', true);
                    submitBtn.find('.glyphicon-refresh.spinning').removeClass('hide');
                }

                if (form.hasClass('rpc')) {
                    var data = form.serializeObject();

                    rpcRequest(form.data('method'), {
                        data: data
                    }, function (response) {
                        // Handles Successful Callback redirect

                        enableSubmit();
                    });
                } else {
                    setTimeout(function () {
                        form[0].submit();
                    }, 100);
                }
            } catch (err) {
                console.log(err);
            }
        }
    });

});