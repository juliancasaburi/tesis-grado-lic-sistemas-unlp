const http = require('http');

// Simulated response data
const simulatedResponse = (id) => ({
    userId: Math.floor(Math.random() * 10) + 1,
    id: id,
    title: `Task ${id}`,
    completed: Math.random() > 0.5  // Randomly true or false
});

// Simulate API request with a fixed duration
const simulateRequest = (id) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(simulatedResponse(id));
        }, 50); // Simulated delay of 50 ms
    });
};

// Create the server
const server = http.createServer(async (req, res) => {
    // Check if the request is a GET to the "/migration-scenario-io-monolithic" route
    if (req.method === 'GET' && req.url === '/migration-scenario-io-monolithic') {
        // Generate three random IDs between 1 and 200
        const randomIds = Array.from({ length: 3 }, () => Math.floor(Math.random() * 200) + 1);

        // Simulate API requests
        try {
            // Simulate all requests in parallel using Promise.all
            const apiResponses = await Promise.all(randomIds.map(id => simulateRequest(id)));

            // Process the responses
            const processedResponses = apiResponses.map(data => {
                return {
                    userId: data.userId,
                    title: data.title.toUpperCase(),  // Convert title to uppercase
                    message: data.completed
                        ? `Task ${data.id} is completed.`
                        : `Task ${data.id} is still pending.`,
                };
            });

            // Return the processed responses as JSON
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(processedResponses));
        } catch (error) {
            // Handle errors during the requests
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: `Error making requests: ${error.message}` }));
        }
    } else {
        // Respond with a 404 if the route is not "/todos"
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Route not found' }));
    }
});

// Start the server on port 3000
server.listen(3000, () => {
    console.log('Server listening on port 3000');
});
