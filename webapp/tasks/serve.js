import gulp from 'gulp'
import browserSync from 'browser-sync'

const TASK_NAME = 'serve'

function serve(){
  gulp.task(TASK_NAME, => {
    browserSync({
      server: {
        baseDir: 'webapp'
      }
    });

    gulp.watch(['public/**/*.js', 'public/**/*.css', 'src/**/*.jsx'], {cwd: 'webapp'});
  });
}
