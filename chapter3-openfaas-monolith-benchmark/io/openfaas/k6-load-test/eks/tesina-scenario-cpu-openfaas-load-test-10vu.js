import http from 'k6/http';

// Endpoints
const functionUrl = 'http://18.231.185.84:31112/function/tesina-scenario-network';

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
  http.get(functionUrl);
}
