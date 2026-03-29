const BASE_URL = "http://localhost:8000";

export async function resetEnv() {
  return fetch(`${BASE_URL}/reset`, { method: "POST" }).then((r) => r.json());
}

export async function getCurrentTicket() {
  return fetch(`${BASE_URL}/current-ticket`).then((r) => r.json());
}

export async function stepEnv(action) {
  return fetch(`${BASE_URL}/step`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(action),
  }).then((r) => r.json());
}

export async function autoStep() {
  return fetch(`${BASE_URL}/auto-step`, {
    method: "POST",
  }).then((r) => r.json());
}

export async function getAnalytics() {
  return fetch(`${BASE_URL}/analytics`).then((r) => r.json());
}