import http from 'k6/http';

export let options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 4000, // RPS
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 4000,
    },
  },
};

export default function () {
  const url = 'https://z29pjrq0rl.execute-api.us-east-1.amazonaws.com/prod/migration-scenario-io-monolithic';

  http.get(url);
}
