import http from 'k6/http';

// Endpoints
const monolithUrl = 'http://18.231.185.84:30000/tesina-scenario-network';

// Options
export const options = {
    scenarios: {
        main_test: {
            executor: 'constant-vus',
            vus: 1,
            duration: '1m',
            exec: 'main',
        }
    }
};

export function main() {
  http.get(monolithUrl);
}