import gulp from "gulp";
import requireDir from "require-dir";
import gulpTaskConfig from "./tasks/libs/gulp-task-config";

gulpTaskConfig(gulp);

requireDir("./tasks");

gulp.config("base.root", "..");
gulp.config("base.src", "./src");
gulp.config("base.dist", "./public");
gulp.config("templates", "../templates");

gulp.config("tasks", requireDir("./tasks/config"));

gulp.config("tasks.build", {
  taskQueue: [
    // 'clean', // Removed because i get this error: EBUSY: resource busy or locked, rmdir '/watcher-app/public/static'
    "copy",
    "sass",
    "server",
    "browserify",
    "revCompile",
    "revReplace"
  ]
});

gulp.task("dev", () => {
  gulp.config(gulp.DEV_MODE, true);
  gulp.start(["build"]);
  gulp.start(["server"]);
});

gulp.task("default", ["build"]);
