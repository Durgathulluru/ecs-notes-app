const textarea = document.getElementById("note");
const clearBtn = document.getElementById("clear-btn");
const saveStatus = document.getElementById("save-status");

if (clearBtn && textarea) {
  clearBtn.addEventListener("click", () => {
    textarea.value = "";
    if (saveStatus) {
      saveStatus.textContent = "Editor cleared locally";
    }
  });
}