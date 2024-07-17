import http from 'k6/http';

// Endpoints
const functionUrl = 'http://ab509d614ff6c41f0ae0acfbe5fdef18-512877466.sa-east-1.elb.amazonaws.com:8080/function/tesina-scenario-cpu';

// Options
export const options = {
    scenarios: {
        main_test: {
            executor: 'constant-vus',
            vus: 20,
            duration: '10m',
            exec: 'main'
        }
    }
};

export function main() {
  http.get(functionUrl);
}
