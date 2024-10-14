const http = require('http');

// Function to validate the incoming request
const validateRequest = (body) => {
    // Check if body is provided and is an object
    if (!body) {
        throw new Error('Request body is missing.');
    }

    const parsedBody = JSON.parse(body);

    // Example validation: Check if `action` and `threshold` are present
    if (!parsedBody.action || typeof parsedBody.action !== 'string') {
        throw new Error('Missing or invalid "action" field.');
    }

    if (!parsedBody.threshold || typeof parsedBody.threshold !== 'number') {
        throw new Error('Missing or invalid "threshold" field.');
    }

    return parsedBody;
};

// Function to simulate a database query with a delay
const simulateDBQuery = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            // Simulate a result set from a database query (array of objects)
            const dbResult = [
                { id: 1, value: 10 },
                { id: 2, value: 20 },
                { id: 3, value: 30 },
                { id: 4, value: 40 },
                { id: 5, value: 50 },
            ];
            resolve(dbResult);
        }, 100);  // Simulates the delay of a DB query (100 ms)
    });
};

// Create an HTTP server
const server = http.createServer(async (req, res) => {
    // Check if the requested URL is the specified endpoint and if it's a POST request
    if (req.url === '/migration-scenario-diurnal-nocturnal-scaling-monolithic' && req.method === 'POST') {
        let body = '';

        // Collect the data from the request
        req.on('data', chunk => {
            body += chunk.toString(); // Convert Buffer to string
        });

        req.on('end', async () => {
            try {
                // Step 1: Validate the request
                const requestData = validateRequest(body);

                // Step 2: Simulate fetching data from the database
                const dbResult = await simulateDBQuery();

                // Step 3: Small processing: Filter and sum the values of objects above the threshold from the request
                const filteredResults = dbResult.filter(item => item.value > requestData.threshold);
                const totalValue = filteredResults.reduce((sum, item) => sum + item.value, 0);

                // Send the response
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    action: requestData.action,
                    dbResult: dbResult,
                    filteredResults: filteredResults,
                    totalValue: totalValue,
                }));
            } catch (error) {
                // Handle errors
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    message: `Error: ${error.message}`
                }));
            }
        });
    } else {
        // Handle unsupported HTTP methods or wrong endpoint
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'Not Found' }));
    }
});

// Start the server
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}/migration-scenario-io-diurnal-nocturnal-scaling-monolithic`);
});
