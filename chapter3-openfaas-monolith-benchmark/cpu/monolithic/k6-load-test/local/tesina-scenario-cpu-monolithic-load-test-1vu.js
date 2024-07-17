import http from 'k6/http';

// Endpoints
const monolithUrl = 'http://127.0.0.1:3000/tesina-scenario-cpu';

// Options
export const options = {
    scenarios: {
        main_test: {
            executor: 'constant-vus',
            vus: 1,
            duration: '10m',
            exec: 'main',
        }
    }
};

export function main() {
  http.get(monolithUrl);
}
