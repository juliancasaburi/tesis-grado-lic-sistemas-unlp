import http from 'k6/http';

// Endpoints
const monolithUrl = 'http://a9d34c07e29194986bc7d82a9abbcc5a-973474190.sa-east-1.elb.amazonaws.com:3000/tesina-scenario-cpu';

// Options
export const options = {
    scenarios: {
        main_test: {
            executor: 'constant-vus',
            vus: 10,
            duration: '10m',
            exec: 'main'
        }
    }
};

export function main() {
  http.get(monolithUrl);
}
