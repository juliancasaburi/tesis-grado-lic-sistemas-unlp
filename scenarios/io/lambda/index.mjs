import { DynamoDBClient, PutItemCommand, GetItemCommand } from '@aws-sdk/client-dynamodb';
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb';
import { v4 as uuidv4 } from 'uuid';

const dynamoDB = new DynamoDBClient({ region: 'sa-east-1' }); // Sao Paulo region

export const handler = async (event) => {
    try {
        // Read the record with UUID e6bdfce3-50ab-4e35-82f7-a0ea0012539c from DynamoDB
        const readParams = {
            TableName: 'TesinaNetworkScenarioLambda',
            Key: marshall({
                id: 'e6bdfce3-50ab-4e35-82f7-a0ea0012539c'
            })
        };

        const { Item: existingItem } = await dynamoDB.send(new GetItemCommand(readParams));

        if (!existingItem) {
            return { error: 'Item not found' };
        }

        // Generate a new UUID for the random value
        const newUUID = uuidv4();

        // Writing a new random value to DynamoDB with the newly generated UUID
        const randomValue = Math.floor(Math.random() * 100);
        const putParams = {
            TableName: 'TesinaNetworkScenarioLambda',
            Item: marshall({
                id: newUUID,
                value: randomValue
            })
        };

        await dynamoDB.send(new PutItemCommand(putParams));

        // Reading the value that was just written
        const getParamsNew = {
            TableName: 'TesinaNetworkScenarioLambda',
            Key: marshall({
                id: newUUID
            })
        };

        const { Item: newItem } = await dynamoDB.send(new GetItemCommand(getParamsNew));
        const writtenValue = unmarshall(newItem);

        return writtenValue;
    } catch (error) {
        console.error('Error:', error);
        return { error: 'Internal Server Error' };
    }
};
