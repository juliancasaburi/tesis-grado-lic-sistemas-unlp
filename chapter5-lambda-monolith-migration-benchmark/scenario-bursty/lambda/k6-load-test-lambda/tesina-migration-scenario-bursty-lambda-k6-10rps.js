import http from 'k6/http';

export let options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 10, // RPS
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 100,
    },
  },
};

export default function () {
  const url = 'https://on1bd49d81.execute-api.us-east-1.amazonaws.com/Prod/tesina-migration-scenario-bursty-lambda';

  http.get(url);
}
