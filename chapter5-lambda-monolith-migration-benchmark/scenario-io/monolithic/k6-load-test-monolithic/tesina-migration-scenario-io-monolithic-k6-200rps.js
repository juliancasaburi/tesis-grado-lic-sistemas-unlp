import http from 'k6/http';

export let options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 200, // RPS
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 40,
      maxVUs: 200,
    },
  },
};

export default function () {
  const url = 'https://0fps2iov0k.execute-api.us-east-1.amazonaws.com/prod/migration-scenario-io-monolithic';

  http.get(url);
}