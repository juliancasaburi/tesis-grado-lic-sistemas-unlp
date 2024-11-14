module.exports = {
  apps: [
    {
      name: 'tesina-migration-scenario-long-running-monolithic',
      script: 'app.mjs',
      instances: 1, // Use a single instance
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
