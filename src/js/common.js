"use strict";

const eventBus = new Vue();

Vue.mixin({
    methods: {
        getEventBus() {
            return eventBus;
        },

        rpc(method, params={}) {
            let self = this;

            return new Promise(function(resolve, reject) {

                let data = JSON.stringify({
                    jsonrpc: '2.0',
                    method: method,
                    params: params,
                    id: 1
                });

                self.getEventBus().$emit('loader-on');
                $.post('/rpc', data, 'json')
                    .done(function (resp) {
                        if (resp.error) {
                            if (resp.error.code == -32000) {
                                self.alert(resp.error.message, resp.error.data || '', 'danger');
                            }
                            reject(resp.error);
                        } else {
                            resolve(resp.result);
                        }
                    })
                    .fail(function (error) {
                        reject(error);
                        self.alert(error.status, error.statusText, 'danger');
                    })
                    .always(function (resp) {
                        self.getEventBus().$emit('loader-off');
                    });
            });
        },

        cleanErrors(errors) {
            let clean = {};

            for (let key in errors) {
                if (typeof errors[key] == 'string') {
                    clean[key] = errors[key];
                } else if (Array.isArray(errors[key])) {
                    clean[key] = errors[key].join(', ');
                } else {
                    clean[key] = this.cleanErrors(errors[key]);
                }
            }

            return clean;
        },

        alert(title, detail, type) {
            this.getEventBus().$emit('message', {
                title: title,
                detail: detail || '',
                type: type || 'info'
            });

        }
    }
});