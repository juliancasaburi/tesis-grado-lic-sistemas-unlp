'use strict';

const {
   DynamoDBClient,
   PutItemCommand,
   GetItemCommand
} = require('@aws-sdk/client-dynamodb');
const {
   marshall,
   unmarshall
} = require('@aws-sdk/util-dynamodb');
const {
   v4: uuidv4
} = require('uuid');
const fs = require('fs');
const path = require('path');

function getSecret(key) {
    const secretFilePath = path.join('/var/openfaas/secrets', key);
    try {
        const secretValue = fs.readFileSync(secretFilePath, 'utf8').trim();
        return secretValue;
    } catch (error) {
        console.error(`Error reading secret ${key}: ${error.message}`);
        return null;
    }
}

const dynamoDB = new DynamoDBClient({
  region: "sa-east-1", // Sao Paulo region
  credentials: {
    accessKeyId: getSecret('dynamodb-access-key-id'),
    secretAccessKey: getSecret('dynamodb-secret-access-key'),
  }
});


module.exports = async (event, context) => {
    try {
        // Read the record with UUID e6bdfce3-50ab-4e35-82f7-a0ea0012539c from DynamoDB
        const readParams = {
            TableName: 'TesinaNetworkScenarioOpenFaaS',
            Key: marshall({
                id: 'e6bdfce3-50ab-4e35-82f7-a0ea0012539c'
            })
        };

        const { Item: existingItem } = await dynamoDB.send(new GetItemCommand(readParams));

        if (!existingItem) {
            return context
                .status(404)
                .fail({ error: 'Item not found' });
        }

        // Generate a new UUID for the random value
        const newUUID = uuidv4();

        // Writing a new random value to DynamoDB with the newly generated UUID
        const randomValue = Math.floor(Math.random() * 100);
        const putParams = {
            TableName: 'TesinaNetworkScenarioOpenFaaS',
            Item: marshall({
                id: newUUID,
                value: randomValue
            })
        };

        await dynamoDB.send(new PutItemCommand(putParams));

        const result = {
            'body': JSON.stringify({
                id: newUUID,
                value: randomValue
            }),
            'content-type': 'application/json'
        };

        return context
            .status(200)
            .succeed(result);

    } catch (error) {
        console.error('Error:', error);
        return context
            .status(500)
            .fail({ error: 'Internal Server Error' });
    }
};
