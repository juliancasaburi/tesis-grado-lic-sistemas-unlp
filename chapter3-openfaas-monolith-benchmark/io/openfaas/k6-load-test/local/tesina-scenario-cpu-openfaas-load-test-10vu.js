import http from 'k6/http';

// Endpoints
const functionUrl = 'http://127.0.0.1:8081/function/tesina-scenario-cpu';

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
