exports.lambdaHandler = async (event) => {
    try {
        const body = event.body ? JSON.parse(event.body) : {};
        const text = body.text || '';

        const encodedText = Buffer.from(text).toString('base64');

        const response = {
            statusCode: 200,
            body: JSON.stringify({
                encoded_text: encodedText
            })
        };

        return response;
    } catch (err) {
        console.error(err);
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: 'Internal server error'
            })
        };
    }
};
