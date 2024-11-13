import { DynamoDBClient, PutItemCommand, GetItemCommand } from '@aws-sdk/client-dynamodb';
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb';
import { v4 as uuidv4 } from 'uuid';

// Initialize the DynamoDB client for the São Paulo region
const dynamoDB = new DynamoDBClient({ region: 'sa-east-1' });

export const handler = async (event) => {
    try {
        // Read the record with a specific UUID from DynamoDB
        const readParams = {
            TableName: 'TesinaNetworkScenarioLambda',
            Key: marshall({
                id: 'e6bdfce3-50ab-4e35-82f7-a0ea0012539c'
            })
        };

        const { Item: existingItem } = await dynamoDB.send(new GetItemCommand(readParams));

        if (!existingItem) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'Item not found' }),
            };
        }

        // Generate a new UUID for the random value
        const newUUID = uuidv4();

        // Write a new random value to DynamoDB with the newly generated UUID
        const randomValue = Math.floor(Math.random() * 100);
        const putParams = {
            TableName: 'TesinaNetworkScenarioLambda',
            Item: marshall({
                id: newUUID,
                value: randomValue
            })
        };

        await dynamoDB.send(new PutItemCommand(putParams));

        // Read the value that was just written
        const getParamsNew = {
            TableName: 'TesinaNetworkScenarioLambda',
            Key: marshall({
                id: newUUID
            })
        };

        const { Item: newItem } = await dynamoDB.send(new GetItemCommand(getParamsNew));
        const writtenValue = unmarshall(newItem);

        return {
            statusCode: 200,
            body: JSON.stringify(writtenValue),
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Internal Server Error' }),
        };
    }
};
