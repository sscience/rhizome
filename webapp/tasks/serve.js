import gulp from 'gulp'
import gulp-serve from 'gulp-serve'

var gulp = require('gulp');
var serve = require('gulp-serve');

gulp.task('serve', serve('public'));
gulp.task('serve-build', serve(['public', 'build']));
gulp.task('serve-prod', serve({
  root: ['public', 'build'],
  port: 80,
  middleware: function(req, res) {
    // custom optional middleware
  }
}));
