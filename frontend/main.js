import { startGame, choose } from "./api.js";
import { render } from "./ui.js";

let sessionId = null;

async function init() {
  const data = await startGame();

  sessionId = data.session_id;

  render(data.node, data.state, handleChoice);
}

async function handleChoice(index) {
  const data = await choose(sessionId, index);

  render(data.node, data.state, handleChoice);
}

document.getElementById("restart").onclick = init;

// start on load
init()