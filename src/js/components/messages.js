"use strict";

Vue.component('messages', {
    data() {
        return {
            messages: []
        };
    },
    mounted() {
        let self = this;

        this.getEventBus().$on('message', function (data) {
            self.messages.push(data);
            setTimeout(function () {
                self.messages.shift();
            }, data.timeout || 5000);
        });
    },
    template: `
        <div id="global-messages" v-show="messages">
            <div v-for="message in messages" class="alert" :class="['alert-' + message.type]" role="alert">
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>            
                <strong v-text="message.title"></strong> {{ message.detail }}
            </div>
        </div>
    `
});