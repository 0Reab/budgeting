/*
Budgeting app
Handles:
Navigation
Upload loading indicator
Entry parsing
Category dropdowns
*/

// Start everything after the page loads.

document.addEventListener("DOMContentLoaded", () => {
    setupNavigation();
    setupUpload();
    setupEntries();
    setupDropdowns();
});

/* Navigation */

function setupNavigation() {
    const title = document.querySelector(".mc");
    const savedButton = document.getElementById("saved-button");

    if (title) {
        title.addEventListener("click", () => {
            window.location.href = "/";
        });
    }

    if (savedButton) {
        savedButton.addEventListener("click", () => {
            window.location.href = "/saved";
        });
    }
}

// Upload loading indicator

function setupUpload() {
    const uploadForm = document.getElementById("upload-form");
    const uploadButton = document.getElementById("upload-button");
    const uploadStatus = document.getElementById("upload-status");

    if (!uploadForm) {
        return;
    }

    uploadForm.addEventListener("submit", () => {
        if (uploadButton) {
            uploadButton.disabled = true;
            uploadButton.value = "Uploading...";
        }

        if (uploadStatus) {
            uploadStatus.classList.add("visible");
        }
    });
}

/*
Parse and display all entries.
Example input:
ID - 1 | categ - food | name - EVA SARDINA PIKANT 115G | total - 169.99 | qty - 1.0 | date - 20.09.2025.
*/

function setupEntries() {
    const rows = document.querySelectorAll(".entry-row");

    rows.forEach(row => {
        const entry = row.dataset.entry;

        if (!entry) {
            return;
        }

        const fields = parseEntry(entry);
        fillEntry(row, fields);
    });
}

/*
Convert the entry string into an object.
Only the first " - " is treated as the key/value separator.
This means a product name can safely contain " - " itself.
*/

function parseEntry(entry) {
    const fields = {};

    entry.split("|").forEach(field => {
        const separatorIndex = field.indexOf(" - ");

        if (separatorIndex === -1) {
            return;
        }

        const key = field.substring(0, separatorIndex).trim().toLowerCase();
        const value = field.substring(separatorIndex + 3).trim();

        fields[key] = value;
    });

    return fields;
}

// Fill the table with the parsed values.

function fillEntry(row, fields) {
    row.querySelectorAll("[data-field]").forEach(element => {
        const field = element.dataset.field;
        element.textContent = fields[field] || "";
    });

    // Keep the complete product name available as a tooltip while CSS truncates the display.
    const nameCell = row.querySelector(".name-cell");

    if (nameCell && fields.name) {
        nameCell.title = fields.name;
    }

    // If editing is enabled and the entry already has a category, display that category.
    const categoryButton = row.querySelector(".dropbtn");

    if (
        categoryButton &&
        fields.categ &&
        fields.categ !== "None"
    ) {
        categoryButton.textContent = fields.categ;
    }
}

// Category dropdowns

function setupDropdowns() {
    const dropdowns =
    document.querySelectorAll(
        ".dropdown"
    );

    dropdowns.forEach(dropdown => {
        const button =
        dropdown.querySelector(
            ".dropbtn"
        );

        if (!button) {
            return;
        }

        const row = dropdown.closest(".entry-row");
        const hiddenInput = row.querySelector('input[type="hidden"]');

        // * Open / close dropdown.
        button.addEventListener("click", event => {
            event.stopPropagation();
                //* Close all other dropdowns.
                dropdowns.forEach(other => {
                if (other !== dropdown) {
                    other.classList.remove("open");
                }
                });
                dropdown.classList.toggle("open");
            }
        );

    //  * Select category.
    const options = dropdown.querySelectorAll(".dropdown-content a");

    options.forEach(option => { option.addEventListener("click", event => {
        event.preventDefault();
        const category = option.dataset.cat;

        // * Update button text.
        button.textContent = category;

        // * Store category in the hidden
        // * input that gets submitted.
        if (hiddenInput) {
            hiddenInput.value = category;
        }

        // * Close menu immediately.
        dropdown.classList.remove("open");
                }
            );
        });
    });

    // Clicking outside closes all menus.
    document.addEventListener("click", () => {
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove("open");
            });
        }
    );
}
