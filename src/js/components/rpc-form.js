"use strict";

Vue.component('rpc-form', {
    data () {
        return {
            data: {},
            error: {},
            loading: false,
            d: {}
        };
    },
    props: ['method', 'onSuccess', 'onError'],
    methods: {
        submit() {
            let self = this;
            self.loading = true;

            if ($(this.$el).find('.g-recaptcha').length) {
                self.data.recaptcha = grecaptcha.getResponse();
            }

            self.rpc(self.method, {
                data: self.data
            }).then(function (result) {

                if ($.isFunction(self.onSuccess)) {
                    self.onSuccess(self, result);
                }

            }, function (error) {
                if (error.code == -32001) {
                    self.error = self.cleanErrors(error.data);
                }

                if ($.isFunction(self.onError)) {
                    self.onError(error);
                }

            }).then(function () {
                self.loading = false;
            });
        }
    }
});