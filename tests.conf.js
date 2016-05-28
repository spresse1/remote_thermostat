// Karma configuration
// Generated on Tue May 10 2016 20:40:07 GMT-0400 (EDT)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['qunit'],
    
    
    // Plugins to use
    //plugins: ['karma-threshold-reporter'],


    // list of files / patterns to load in the browser
    files: [
      'web_interface/js/*.js',
      'web_interface/tests/tests-qunit.js',
      'lib/node_modules/sinon/pkg/sinon.js',
      'lib/node_modules/jquery/dist/jquery.js',
      
    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'web_interface/js/*.js': ['coverage']
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true,

    // Concurrency level
    // how many browser should be started simultaneous
    concurrency: Infinity,
    
    // Configure coverage to output TYPE to LOCATION
    coverageReporter: {
      type : 'lcovonly',
      subdir: '.',
      file: 'jscover.lcov'
      //dir : 'coverage/'
    },
    
    thresholdReporter: {
      statements: 100,
      branches: 100,
      functions: 100,
      lines: 100
    }
  })
}
