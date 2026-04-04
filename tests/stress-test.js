import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m',  target: 50 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.post('http://localhost:30001/payment',
    JSON.stringify({
      token: 'secret-key-123',
      user_id: 'user1',
      amount: Math.floor(Math.random() * 100) + 1,
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(0.5);
}
