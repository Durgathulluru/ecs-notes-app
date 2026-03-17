const textarea = document.getElementById("note");
const clearBtn = document.getElementById("clear-btn");
const saveStatus = document.getElementById("save-status");
const noteIdInput = document.getElementById("note_id");

if (clearBtn && textarea) {
  clearBtn.addEventListener("click", () => {
    textarea.value = "";
    if (noteIdInput) {
      noteIdInput.value = "";
    }
    if (saveStatus) {
      saveStatus.textContent = "Ready to create a new note";
    }
    window.history.replaceState({}, "", "/");
  });
}