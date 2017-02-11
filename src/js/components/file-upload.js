"use strict";

Vue.component('file-upload', {
    data() {
        return {

        };
    },
    props: ['multiple', 'entityKey', 'entityProp', 'onSuccess', 'accept', 'maxSize'],
    mounted() {
        let self = this;

        $(this.$el).find('input[type=file]').fileupload({
            dataType: 'json',
            formData: {
                key: self.entityKey,
                prop: self.entityProp
            },
            submit (e, data) {
                let $this = $(this);

                self.rpc('create_upload_url', {}).then(function (result) {
                    data.url = result;
                    $this.fileupload('send', data);
                });

                return false;
            },
            done(e, data) {
                if (data.result.error) {
                    self.getEventBus().$emit('message', {
                        title: 'Upload Error',
                        detail: data.result.error,
                        type: 'danger'
                    });
                } else if ($.isFunction(self.onSuccess)) {
                    self.onSuccess(self, data.result.entity);
                }
            },
            add(e, data) {
                if(self.accept && data.originalFiles[0]['type'].length && data.originalFiles[0]['type'].indexOf(self.accept.split('/')[0]) == -1) {
                    self.getEventBus().$emit('message', {
                        title: 'Upload Error',
                        detail: 'Invalid file type',
                        type: 'danger'
                    });
                } else if(self.maxSize && data.originalFiles[0]['size'] && data.originalFiles[0]['size'] > parseInt(self.maxSize)) {
                    self.getEventBus().$emit('message', {
                        title: 'Upload Error',
                        detail: 'File size over ' + parseInt(parseInt(self.maxSize) / 1000000.0) + 'MB',
                        type: 'danger'
                    });
                } else {
                    data.submit();
                }
            },
        });
    },
    template: `
        <label class="upload-button">
            <a class="btn btn-sm pull-right"><i class="fa fa-camera"></i></a>
            <span><input type="file" name="file" v-bind:accept="accept" v-bind:multiple="multiple"></span>
        </label>
        `
});