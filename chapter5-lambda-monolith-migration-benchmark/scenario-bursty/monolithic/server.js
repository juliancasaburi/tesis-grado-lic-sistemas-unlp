const http = require('http');

const fibonacci = (num) => {
    let a = BigInt(1), b = BigInt(0), temp;

    while (num >= 0) {
        temp = a;
        a = a + b;
        b = temp;
        num--;
    }
    return b;
};

// Create the server
const server = http.createServer(async (req, res) => {
    if (req.method === 'GET' && req.url === '/migration-scenario-bursty-monolithic') {
        try {
            const result = fibonacci(100000);

            // Return the processed responses as JSON
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ result: result.toString() }));
        } catch (error) {
            // Handle errors during the requests
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: `Error making requests: ${error.message}` }));
        }
    } else if (req.method === 'GET' && req.url === '/health') {
        // Health check endpoint for AWS Auto Scaling
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'healthy' }));
    } else {
        // Handle 404 for unknown routes
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Route not found' }));
    }
});

// Start the server on port 3000
server.listen(3000, () => {
    console.log('Server listening on port 3000');
});
