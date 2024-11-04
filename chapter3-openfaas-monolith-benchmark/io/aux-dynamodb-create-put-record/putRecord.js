import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
import { marshall } from "@aws-sdk/util-dynamodb";

const client = new DynamoDBClient({ region: "us-east-1" });

async function putInitialRecord() {
    // Define the ID and a random value
    const id = 'e6bdfce3-50ab-4e35-82f7-a0ea0012539c';
    const randomValue = Math.floor(Math.random() * 100);

    // Prepare the put parameters
    const putParams = {
        TableName: 'TesinaNetworkScenarioLambda',
        Item: marshall({
            id: id,
            value: randomValue
        })
    };

    try {
        // Insert the item into DynamoDB
        await client.send(new PutItemCommand(putParams));
        console.log("Item added successfully:", { id, randomValue });
    } catch (error) {
        console.error("Error adding item:", error);
    }
}

putInitialRecord();
