export function render(node, state, onChoice) {
  
  document.getElementById("stats").innerText = `
  HP: ${state.hp}
  Gold: ${state.gold}
  STR: ${state.stats.strength}
  DEX: ${state.stats.dexterity}
  INT: ${state.stats.intelligence}
  FAI: ${state.stats.faith}
  `;

  document.getElementById("story").innerHTML =
    marked.parse(node.text);

  const choicesDiv = document.getElementById("choices");
  choicesDiv.innerHTML = "";

  if (!node.choices || node.choices.length === 0) {
    choicesDiv.innerHTML = "<p><b>Game Over</b></p>";
    return;
  }

  node.choices.forEach((choice, index) => {
    const btn = document.createElement("button");
    btn.innerText = choice.text;

    btn.onclick = () => onChoice(index);

    choicesDiv.appendChild(btn);
    choicesDiv.appendChild(document.createElement("br"));
  });
}