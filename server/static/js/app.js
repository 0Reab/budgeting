/*
Budgeting app
Handles:
Navigation
Upload loading indicator
Entry parsing
Category dropdowns
Select and delete rows in DB
Form for income
*/

const idList = new Set();

// Start everything after the page loads.

document.addEventListener("DOMContentLoaded", () => {
    setupNavigation();
    setupUpload();
    setupEntries();
    setupDropdowns();
    main();
});

function main() {
    let loc = window.location.pathname;

    if (loc === '/show/income') {
        showElementId('edit-button', 'inline', false);
    }

    if (loc === '/show/expenses') {
        showElementId('edit-button', 'inline', false);
        // showElementId('add-income-form');
    }

    if (loc === '/add-income') {
        showElementId('add-income-form');
    }

    // restore scroll on location change
    // Source - https://stackoverflow.com/a/63687846
    // Posted by James Ashwood Retrieved 2026-09-28, License - CC BY-SA 4.0
    window.onunload = function() {
        localStorage.setItem("scrollY", window.scrollY);
    }

    if (window.sessionStorage.getItem("playedAnimation") === null) {
        playAnimations();
    }

    // scroll at the end of everything loading - no lag
    if (loc != '/') {
        showElementId('entries-card', 'block', true);
        element = document.getElementById("entries-card");

        element.classList.add('fade-in-slow');
        element.scrollIntoView({behavior: "smooth"});
    }
}

// helper shorthanders lel

function playAnimations() {
    //document.getElementById("").classList.add("scale-in");
    $('.saved-button').addClass('scale-in');
    $('.card').addClass('scale-in');

    $('.header-text').addClass('scale-in');
    $('.balance').addClass('appear-from-above');
    $('.mc').addClass('appear-from-above');

    window.sessionStorage.setItem("playedAnimation", 1);
}

async function paste(input) {
    const text = await navigator.clipboard.readText();
    input.value = text;
}


function showElementId(name, targetStyle = 'inline', toggle = true) {
    const element = document.getElementById(name);

    if (!element) {
        console.error(`Couldn't find element ${name}.`)
        return;
    } 

    if (!toggle) {
        element.style.display = targetStyle;
        return;
    }
    element.style.display =
        element.style.display === 'none' ? targetStyle : 'none';
}


function showElementsClass(name) {
    let selector = '.' + name;
    let elements = document.querySelectorAll(selector);

    elements.forEach(element => {
        if (element.style.display === 'none') {
            element.style.display = 'table-cell';
            element.classList.add('fade-in');
        } else {
            element.style.display = 'none';
        }
    });
}

function hideElementsClass(name) {
    let selector = '.' + name;
    let elements = document.querySelectorAll(selector);

    elements.forEach(element => {
        element.style.display = 'none';
    })
}

// income form and more

// Deletion

function selectID(element) {
    const id = element.closest('tr').querySelector('.table-value').textContent.trim();

    if (element.checked) {
        idList.add(id);
    } else {
        idList.delete(id);
    }
}

async function deleteSelected() {
    if (idList.size === 0) {
        return;
    }

    const params = new URLSearchParams();
    let url = '/api/delete?';

    for (const id of idList) {
        params.append('id', id);
    }

    const response = await fetch(`${url}${params.toString()}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        console.error('Failed to delete selected IDs');
        return;
    }

    location.reload();
}

/* Navigation */

function setupNavigation() {
    const loc = document.location.pathname;

    const title = document.querySelector(".mc");
    const savedButton = document.getElementById("saved-button");
    const incomeButton = document.getElementById("add-income-button");
    const incomeForm = document.getElementById("add-income-form")
    const submitIncomeButton = document.getElementById("submit-income-button");
    const showIncomeButton = document.getElementById("show-income-button");
    const deleteButton = document.getElementById("delete-button");
    const editButton = document.getElementById("edit-button");
    const balance = document.getElementById("balance");

    if (title) {
        title.addEventListener("click", () => {
            window.location.href = "/";
        });
    }

    if (savedButton) {
        savedButton.addEventListener("click", () => {
            window.location.href = "/show/expenses";
        });
    }

    if (showIncomeButton) {
        showIncomeButton.addEventListener("click", () => {
            window.location.href = "/show/income";
        });
    }

    if (incomeButton) {
        incomeButton.addEventListener("click", () => {
            window.location.href = "/add-income";
        })
    }

    if (deleteButton) {
        deleteButton.addEventListener("click", () => {
            showElementId('undo-button');
            deleteSelected();
        })
    }

    if (editButton) {
        editButton.addEventListener("click", () => {
            showElementId('delete-button');
            showElementsClass('edits');
        })
    }

    if (submitIncomeButton) {
        submitIncomeButton.addEventListener("click", () => {
            incomeForm.submit();
        })
    }

    if (balance) {
        balance.addEventListener("click", () => {
            balance.innerText = 'me change!';
        })
    }

    if (loc === '/show/income') {
        hideElementsClass('tag-wallets');
        hideElementsClass('tag-expenses');
        hideElementsClass('tag-upload');

    } else if (loc === '/show/expenses') {
        hideElementsClass('tag-wallets');
        hideElementsClass('tag-income');
        hideElementsClass('tag-upload');

    } else if (loc === '/upload') {
        hideElementsClass('tag-wallets');
        hideElementsClass('tag-income');
        hideElementsClass('tag-expenses');

    } else if (loc === '/show/wallets') {
        hideElementsClass('tag-upload');
        hideElementsClass('tag-income');
        hideElementsClass('tag-expenses');
    }
/*

    } else if (loc === '/show/wallets') {
        hideElementsClass('tag-income');
        hideElementsClass('tag-expenses');
        hideElementsClass('tag-upload');

    } else if (loc === '/upload') {
        hideElementsClass('tag-income');
        hideElementsClass('tag-expenses');
        hideElementsClass('tag-wallets');
    }
*/
    if (loc != '/') {
        document.getElementById("myChartScroll").style.display = 'inline';
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
