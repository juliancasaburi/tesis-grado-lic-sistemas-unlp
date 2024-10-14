exports.handler = async (event) => {
    const fibonacci = (num) => {
        let a = BigInt(1), b = BigInt(0), temp;

        while (num >= 0) {
            temp = a;
            a = a + b;
            b = temp;
            num--;
        }
        return b;
    };

    const result = fibonacci(100000);

    return {
        statusCode: 200,
        body: JSON.stringify({ result: result.toString() }),
    };
};
