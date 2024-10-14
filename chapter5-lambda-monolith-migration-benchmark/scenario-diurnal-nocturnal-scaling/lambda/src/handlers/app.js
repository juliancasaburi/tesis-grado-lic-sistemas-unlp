exports.handler = async (event) => {

    // Simulated request validation
    const validateRequest = (event) => {
        const { body } = event;

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

    // Simulate a database query with a delay
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

    try {
        // Step 1: Validate the request
        const requestData = validateRequest(event);

        // Step 2: Simulate fetching data from the database
        const dbResult = await simulateDBQuery();

        // Step 3: Small processing: Filter and sum the values of objects above the threshold from the request
        const filteredResults = dbResult.filter(item => item.value > requestData.threshold);
        const totalValue = filteredResults.reduce((sum, item) => sum + item.value, 0);

        return {
            statusCode: 200,
            body: JSON.stringify({
                action: requestData.action,
                dbResult: dbResult,
                filteredResults: filteredResults,
                totalValue: totalValue,
            }),
        };
    } catch (error) {
        return {
            statusCode: 400,
            body: JSON.stringify({
                message: `Error: ${error.message}`
            }),
        };
    }
};
