import http from 'k6/http';

export let options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 2000, // RPS
      timeUnit: '1s',
      duration: '7m30s',
      preAllocatedVUs: 4000,
    },
  },
};

export default function () {
  const url = 'https://h15k89715c.execute-api.us-east-1.amazonaws.com/prod/migration-scenario-diurnal-nocturnal-scaling-monolithic';
  const payload = JSON.stringify({
    action: "sumAboveThreshold",
    threshold: 25,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  http.post(url, payload, params);
}
