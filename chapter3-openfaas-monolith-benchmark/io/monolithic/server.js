'use strict';

const express = require('express');
const { DynamoDBClient, PutItemCommand, GetItemCommand } = require('@aws-sdk/client-dynamodb');
const { marshall, unmarshall } = require('@aws-sdk/util-dynamodb');
const { v4: uuidv4 } = require('uuid');

require("dotenv").config(); // read .env

const app = express();

const dynamoDB = new DynamoDBClient({
  region: "sa-east-1", // Sao Paulo region
  credentials: {
    accessKeyId: process.env.DYNAMODB_ACCESS_KEY_ID,
    secretAccessKey: process.env.DYNAMODB_SECRET_ACCESS_KEY,
  }
});

app.get('/tesina-scenario-network', async (req, res) => {
    try {
        // Read the record with UUID e6bdfce3-50ab-4e35-82f7-a0ea0012539c from DynamoDB
        const readParams = {
            TableName: 'TesinaNetworkScenarioMonolithic',
            Key: marshall({
                id: 'e6bdfce3-50ab-4e35-82f7-a0ea0012539c'
            })
        };

        const { Item: existingItem } = await dynamoDB.send(new GetItemCommand(readParams));

        if (!existingItem) {
            return res.status(404).json({ error: 'Item not found' });
        }

        // Generate a new UUID for the random value
        const newUUID = uuidv4();

        // Writing a new random value to DynamoDB with the newly generated UUID
        const randomValue = Math.floor(Math.random() * 100);
        const putParams = {
            TableName: 'TesinaNetworkScenarioMonolithic',
            Item: marshall({
                id: newUUID,
                value: randomValue
            })
        };

        await dynamoDB.send(new PutItemCommand(putParams));

        // Respond with the newly written item
        res.json({ id: newUUID, value: randomValue });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});


const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
