const textarea = document.getElementById("note");
const statusEl = document.getElementById("autosave-status");
const clearBtn = document.getElementById("clear-btn");

let autosaveTimer = null;
let lastSentValue = window.NOTES_APP?.initialText || "";

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b91c1c" : "#065f46";
}

async function autoSaveDraft() {
  const currentValue = textarea.value;

  if (currentValue === lastSentValue) {
    return;
  }

  try {
    const response = await fetch("/autosave", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        note_text: currentValue
      })
    });

    if (!response.ok) {
      throw new Error("Auto-save failed");
    }

    const data = await response.json();
    lastSentValue = currentValue;
    setStatus("Last auto-saved: " + data.updated_at);
  } catch (error) {
    setStatus("Auto-save error", true);
  }
}

textarea.addEventListener("input", () => {
  setStatus("Typing...");

  if (autosaveTimer) {
    clearInterval(autosaveTimer);
  }

  autosaveTimer = setInterval(autoSaveDraft, 3000);
});

clearBtn.addEventListener("click", () => {
  textarea.value = "";
  setStatus("Draft cleared locally");
});

window.addEventListener("beforeunload", () => {
  if (textarea.value !== lastSentValue) {
    navigator.sendBeacon(
      "/autosave-beacon",
      new Blob(
        [JSON.stringify({ note_text: textarea.value })],
        { type: "application/json" }
      )
    );
  }
});