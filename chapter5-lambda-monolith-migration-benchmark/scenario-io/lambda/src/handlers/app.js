const simulatedResponse = (id) => ({
    userId: Math.floor(Math.random() * 10) + 1,
    id: id,
    title: `Task ${id}`,
    completed: Math.random() > 0.5  // Randomly true or false
});

exports.handler = async (event) => {
    // Generate three random IDs between 0 and 200
    const randomIds = Array.from({ length: 3 }, () => Math.floor(Math.random() * 201));

    // Simulate API request with a fixed duration
    const simulateRequest = (id) => {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(simulatedResponse(id));
            }, 50); // Simulated delay of 50 ms
        });
    };

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

        // Return the processed responses
        return {
            statusCode: 200,
            body: JSON.stringify(processedResponses)
        };

    } catch (error) {
        // Handle any errors
        return {
            statusCode: 500,
            body: JSON.stringify(`Error making requests: ${error.message}`)
        };
    }
};
