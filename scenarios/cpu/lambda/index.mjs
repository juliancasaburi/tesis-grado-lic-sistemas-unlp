'use strict';

// Sieve of Eratosthenes algorithm to generate prime numbers
function generatePrimes(n) {
    const primes = [];
    const sieve = Array(n + 1).fill(true);
    sieve[0] = false;
    sieve[1] = false;

    for (let p = 2; p * p <= n; p++) {
        if (sieve[p] === true) {
            for (let i = p * p; i <= n; i += p) {
                sieve[i] = false;
            }
        }
    }

    for (let i = 2; i <= n; i++) {
        if (sieve[i] === true) {
            primes.push(i);
        }
    }

    return primes;
}

export async function handler(event, context) {
    const primes = generatePrimes(10000);

    const result = {
        'body': JSON.stringify(primes),
        'headers': {
            'Content-Type': 'application/json'
        },
        'statusCode': 200
    };

    return result;
}
