"use strict";

Vue.component('loader', {
    data() {
        return {
            show: true
        };
    },
    mounted() {
        this.getEventBus().$on('loader-on', () => this.show = true);
        this.getEventBus().$on('loader-off', () => this.show = false);
    },
    template: `
        <div id="loader" v-show="show">
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
        </div>
    `
});