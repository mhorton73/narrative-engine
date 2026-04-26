
const BASE_URL = "http://localhost:8000";

export async function startGame() {
  const res = await fetch(`${BASE_URL}/start`, {
    method: "POST"
  });

  return await res.json();
}

export async function choose(sessionId, index) {
  const res = await fetch(
    `${BASE_URL}/choose?session_id=${sessionId}&choice_index=${index}`,
    { method: "POST" }
  );

  return await res.json();
}