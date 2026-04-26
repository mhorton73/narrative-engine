export function render(node, onChoice) {
  document.getElementById("story").innerText = node.text;

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