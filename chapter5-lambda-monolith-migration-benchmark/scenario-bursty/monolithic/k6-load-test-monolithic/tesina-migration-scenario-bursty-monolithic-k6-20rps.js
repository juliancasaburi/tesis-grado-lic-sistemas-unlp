import http from 'k6/http';

export let options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 20, // RPS
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 100,
    },
  },
};

export default function () {
  const url = 'https://4k5wz4qc6f.execute-api.us-east-1.amazonaws.com/prod/migration-scenario-bursty-monolithic';

  http.get(url);
}
