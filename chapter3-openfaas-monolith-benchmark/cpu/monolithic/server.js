'use strict';

const express = require('express');
const app = express();

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

app.get('/tesina-scenario-cpu', async (req, res) => {
    const primes = generatePrimes(2000000);

    const result = {
        'body': primes,
        'content-type': 'application/json'
    };

    res.status(200).json(result);
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
