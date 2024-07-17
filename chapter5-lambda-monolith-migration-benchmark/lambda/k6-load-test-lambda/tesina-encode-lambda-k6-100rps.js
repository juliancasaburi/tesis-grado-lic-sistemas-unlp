import http from 'k6/http';

export let options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 100, // RPS
      timeUnit: '1s',
      duration: '1m',
      preAllocatedVUs: 20,
      maxVUs: 100,
    },
  },
};

export default function () {
  const url = 'https://bvazo3cbx9.execute-api.us-east-1.amazonaws.com/Prod/tesina-encode-lambda';
  const payload = JSON.stringify({ text: 'Hello, World!' });
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  http.post(url, payload, params);
}
