const http = require('http');

const port = 3000;

const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/encode') {
        let body = '';

        req.on('data', chunk => {
            body += chunk.toString();
        });

        req.on('end', () => {
            try {
                const parsedBody = body ? JSON.parse(body) : {};
                const text = parsedBody.text || '';

                const encodedText = Buffer.from(text).toString('base64');

                const response = {
                    body: JSON.stringify({
                        encoded_text: encodedText
                    })
                };

                res.writeHead(200, {'Content-Type': 'application/json'});
                res.end(JSON.stringify(response));
            } catch (err) {
                console.error(err);
                res.writeHead(500, {'Content-Type': 'application/json'});
                res.end(JSON.stringify({
                    message: 'Internal server error'
                }));
            }
        });
    } else {
        res.writeHead(404, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({
            message: 'Not Found'
        }));
    }
});

server.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
