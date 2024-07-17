module.exports = {
  apps: [
    {
      name: 'tesina-encode-monolithic',
      script: 'server.js',
      instances: 'max',   // Run as many instances as the number of CPU cores
      exec_mode: 'cluster', // Enable clustering to utilize multiple CPU cores
      out_file: '/dev/null', // Disable logging
      error_file: '/dev/null', // Disable logging
      watch: 'false', // Disable watch mode
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
};
