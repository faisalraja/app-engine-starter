"use strict";
import "./common";
import "./components/loader";
import "./components/rpc-form";
import "./components/messages";
import "./components/file-upload";
import "./page/post"

$(document).ready(function(){
    const appData = window.appData || {};

    new Vue({
        el: '#app',
        replace: false,
        data: {},

        mounted() {
            let self = this,
                eventBus = self.getEventBus();

            eventBus.$emit('loader-off');

            if (Array.isArray(appData.globalMessages) && appData.globalMessages.length) {
                for (let message of appData.globalMessages) {
                    self.alert(message[0], null, message[1]);
                }
            }

            $(this.$el).find('.init-hide').removeClass('init-hide');
        }
    });
});