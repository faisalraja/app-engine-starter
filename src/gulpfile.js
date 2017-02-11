const gulp =require('gulp');
const watch = require('gulp-watch');
const sass = require('gulp-sass');
const cleanCSS = require('gulp-clean-css');
const minifyJS = require('gulp-js-minify');
const rename = require("gulp-rename");
const runSequence = require('run-sequence');
const babel = require('gulp-babel');
const rollup = require('gulp-rollup');

const buildCss = function (env) {
    const s = sass();

    s.on('error',function(e){
        console.error(e);
        s.end();
    });

    const content = gulp.src('scss/*.scss')
        .pipe(s)
        .pipe(cleanCSS());

    return content.pipe(gulp.dest('../static/css/dist/'));
};

const buildJs = function (env) {
    const content = gulp.src(['js/**/*.js'])
        .pipe(rollup({
            entry: [
                './js/main.js'
            ]
        }))
        .pipe(babel({
            "presets": [
                "es2015"
            ],
            "plugins": [
                "transform-async-to-module-method",
                "syntax-async-functions"
            ]
        }));

    if (env != 'dev') {
        content
            .pipe(minifyJS())
            .pipe(rename({ suffix: '.min' }))
    }

    return content.pipe(gulp.dest('../static/js/dist/'));
};

gulp.task('watch', function() {
    runSequence('copy-lib', 'build', () => {
        "use strict";

        gulp.watch('scss/**/*.scss', ['build-css']);
        gulp.watch('js/**/*.js', ['build-js']);
    });
});

gulp.task('build-css', function(){
    return buildCss('development');
});

gulp.task('build-js', function() {
    return buildJs('dev');
});

gulp.task('build-prod', function () {
    buildCss('prod');
    buildJs('prod');
});

gulp.task('copy-lib', function(){
    gulp.src([
        'node_modules/jquery/dist/jquery.min.js',
        'node_modules/vue/dist/vue.min.js',
        'node_modules/vue/dist/vue.min.js.map',
        'node_modules/tether/dist/js/tether.min.js',
        'node_modules/bootstrap/dist/js/bootstrap.min.js',
        'node_modules/blueimp-file-upload/js/jquery.fileupload.js',
        'node_modules/blueimp-file-upload/js/jquery.iframe-transport.js',
        'node_modules/jquery-ui/ui/widget.js'
    ]).pipe(gulp.dest('../static/js/dist'));

    gulp.src([
        'node_modules/font-awesome/fonts/*'
    ]).pipe(gulp.dest('../static/css/dist/fonts/'));
});

gulp.task('build', function(cb) {
    runSequence(
        'build-css',
        'build-js',
        cb);
});