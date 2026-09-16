console.log("ShadowShield content script loaded.");

let shadowShieldChecking = false;

// This flag allows a send that ShadowShield has already approved.
// It prevents our own programmatic send click from being
// intercepted for a second time.
let allowNextSend = false;


// ============================================================
// FIND CHATGPT PROMPT BOX
// ============================================================

function findPromptBox() {

    const editor = document.querySelector(
        "div[contenteditable='true'].ProseMirror"
    );

    if (editor) {
        return editor;
    }

    return document.querySelector(
        "div[contenteditable='true']"
    );
}


// ============================================================
// GET PROMPT TEXT
// ============================================================

function getPromptText(editor) {

    if (!editor) {
        return "";
    }

    return editor.innerText.trim();
}


// ============================================================
// SEND PROMPT TO FASTAPI
// ============================================================

function sendForAnalysis(text) {

    return new Promise((resolve) => {

        chrome.runtime.sendMessage(
            {
                type: "ANALYZE_PROMPT",
                text: text
            },

            response => {

                if (chrome.runtime.lastError) {

                    console.error(
                        "ShadowShield API error:",
                        chrome.runtime.lastError.message
                    );

                    resolve(null);
                    return;
                }

                resolve(response);
            }
        );
    });
}


// ============================================================
// REPLACE CHATGPT EDITOR CONTENT
// ============================================================

function replaceEditorText(editor, newText) {

    if (!editor) {
        return false;
    }

    editor.focus();

    const selection = window.getSelection();

    const range = document.createRange();

    range.selectNodeContents(editor);

    selection.removeAllRanges();

    selection.addRange(range);


    let success = false;

    try {

        success = document.execCommand(
            "insertText",
            false,
            newText
        );

    } catch (error) {

        console.warn(
            "ShadowShield execCommand failed:",
            error
        );

    }


    // Fallback
    if (!success) {

        editor.textContent = newText;

        editor.dispatchEvent(
            new InputEvent(
                "input",
                {
                    bubbles: true,
                    inputType: "insertText",
                    data: newText
                }
            )
        );
    }


    // Notify ChatGPT/React that the editor changed
    editor.dispatchEvent(
        new InputEvent(
            "input",
            {
                bubbles: true,
                inputType: "insertText",
                data: newText
            }
        )
    );


    editor.dispatchEvent(
        new Event(
            "change",
            {
                bubbles: true
            }
        )
    );


    return true;
}


// ============================================================
// FIND CHATGPT SEND BUTTON
// ============================================================

function findSendButton() {

    let button = document.querySelector(
        "button[data-testid='send-button']"
    );

    if (button) {
        return button;
    }


    const buttons =
        document.querySelectorAll("button");


    for (const candidate of buttons) {

        const label =
            (
                candidate.getAttribute(
                    "aria-label"
                ) || ""
            ).toLowerCase();


        const testId =
            candidate.getAttribute(
                "data-testid"
            ) || "";


        if (
            testId === "send-button"
            ||
            label.includes("send")
        ) {

            return candidate;
        }
    }


    return null;
}


// ============================================================
// SEND TO CHATGPT
// ============================================================

function clickChatGPTSend() {

    const sendButton =
        findSendButton();


    if (!sendButton) {

        console.warn(
            "ShadowShield: Send button not found."
        );

        return false;
    }


    if (sendButton.disabled) {

        console.warn(
            "ShadowShield: Send button is disabled."
        );

        return false;
    }


    console.log(
        "ShadowShield: Sending approved prompt."
    );


    // IMPORTANT:
    // Tell our document click handler that this next
    // send click is intentional.
    allowNextSend = true;


    setTimeout(() => {

        const currentButton =
            findSendButton();


        if (!currentButton) {

            console.warn(
                "ShadowShield: Send button disappeared."
            );

            allowNextSend = false;

            return;
        }


        if (currentButton.disabled) {

            console.warn(
                "ShadowShield: Send button became disabled."
            );

            allowNextSend = false;

            return;
        }


        currentButton.click();


        // Safety reset
        setTimeout(() => {

            allowNextSend = false;

        }, 1000);

    }, 500);


    return true;
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


// ============================================================
// REMOVE WARNING
// ============================================================

function removeWarning() {

    const overlay =
        document.getElementById(
            "shadowshield-warning"
        );


    if (overlay) {

        overlay.remove();

        console.log(
            "ShadowShield: Warning removed."
        );
    }
}


// ============================================================
// SHOW WARNING
// ============================================================

function showWarning(
    result,
    editor
) {

    // Remove previous warning
    removeWarning();


    const overlay =
        document.createElement("div");


    overlay.id =
        "shadowshield-warning";


    // IMPORTANT:
    // Prevent clicks inside our warning from reaching
    // ChatGPT's document-level click handlers.
    overlay.addEventListener(
        "click",
        event => {

            event.stopPropagation();

        }
    );


    const detectionList =
        result.detections
            .map(
                detection =>
                    `<div>
                        • ${escapeHtml(
                            detection.type
                        )}
                    </div>`
            )
            .join("");


    overlay.innerHTML = `

        <div class="shadowshield-card">

            <div class="shadowshield-title">
                ⚠️ ShadowShield Warning
            </div>

            <div class="shadowshield-message">
                Sensitive information was detected
                in your prompt.
            </div>

            <div class="shadowshield-risk">
                Risk Level:
                <strong>
                    ${escapeHtml(
                        result.risk_level
                    )}
                </strong>
            </div>

            <div class="shadowshield-detections">

                ${detectionList}

            </div>

            <div class="shadowshield-preview">

                <strong>
                    Redacted version:
                </strong>

                <div class="shadowshield-text">
                    ${escapeHtml(
                        result.redacted_text
                    )}
                </div>

            </div>

            <div class="shadowshield-buttons">

                <button
                    type="button"
                    id="shadowshield-redact"
                    class="shadowshield-primary">
                    Redact & Send
                </button>

                <button
                    type="button"
                    id="shadowshield-edit">
                    Edit
                </button>

                <button
                    type="button"
                    id="shadowshield-send">
                    Send Anyway
                </button>

                <button
                    type="button"
                    id="shadowshield-cancel">
                    Cancel
                </button>

            </div>

        </div>
    `;


    document.body.appendChild(
        overlay
    );


    // ========================================================
    // REDACT & SEND
    // ========================================================

    document
        .getElementById(
            "shadowshield-redact"
        )
        .addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();

                console.log(
                    "ShadowShield: Redact & Send clicked."
                );


                // Replace original prompt
                const replaced =
                    replaceEditorText(
                        editor,
                        result.redacted_text
                    );


                if (!replaced) {

                    console.error(
                        "ShadowShield: Could not update editor."
                    );

                    return;
                }


                console.log(
                    "ShadowShield: Prompt replaced with redacted text."
                );


                // Close warning BEFORE sending
                removeWarning();


                // Give ChatGPT time to update its internal
                // editor state.
                setTimeout(() => {

                    clickChatGPTSend();

                }, 300);

            }
        );


    // ========================================================
    // EDIT
    // ========================================================

    document
        .getElementById(
            "shadowshield-edit"
        )
        .addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();

                console.log(
                    "ShadowShield: Edit clicked."
                );


                removeWarning();


                // Leave the current prompt in the editor
                // so the user can manually edit it.
                setTimeout(() => {

                    const currentEditor =
                        findPromptBox();

                    if (currentEditor) {
                        currentEditor.focus();
                    }

                }, 100);

            }
        );


    // ========================================================
    // SEND ANYWAY
    // ========================================================

    document
        .getElementById(
            "shadowshield-send"
        )
        .addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();

                console.log(
                    "ShadowShield: Send Anyway clicked."
                );


                removeWarning();


                setTimeout(() => {

                    clickChatGPTSend();

                }, 200);

            }
        );


    // ========================================================
    // CANCEL
    // ========================================================

    document
        .getElementById(
            "shadowshield-cancel"
        )
        .addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();

                console.log(
                    "ShadowShield: Cancel clicked."
                );


                // Just close the warning.
                // Do NOT send anything.
                removeWarning();

            }
        );
}


// ============================================================
// ANALYZE PROMPT
// ============================================================

async function analyzeCurrentPrompt() {

    if (shadowShieldChecking) {

        console.log(
            "ShadowShield: Already checking a prompt."
        );

        return;
    }


    const editor =
        findPromptBox();


    if (!editor) {

        console.warn(
            "ShadowShield: Prompt editor not found."
        );

        return;
    }


    const text =
        getPromptText(editor);


    if (!text) {
        return;
    }


    shadowShieldChecking = true;


    console.log(
        "ShadowShield: Analyzing prompt..."
    );


    const response =
        await sendForAnalysis(text);


    shadowShieldChecking = false;


    if (!response || !response.success) {

        console.error(
            "ShadowShield: Analysis failed."
        );

        return;
    }


    const result =
        response.data;


    console.log(
        "ShadowShield analysis:",
        result
    );


    // ========================================================
    // SAFE
    // ========================================================

    if (
        result.risk_level === "SAFE"
    ) {

        console.log(
            "ShadowShield: SAFE → allowing submission."
        );


        clickChatGPTSend();

        return;
    }


    // ========================================================
    // SENSITIVE / HIGH RISK
    // ========================================================

    showWarning(
        result,
        editor
    );
}


// ============================================================
// KEYBOARD INTERCEPTION
// ============================================================

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
            &&
            !event.shiftKey
        ) {

            const editor =
                findPromptBox();


            if (!editor) {
                return;
            }


            const text =
                getPromptText(editor);


            if (!text) {
                return;
            }


            console.log(
                "ShadowShield: Enter intercepted."
            );


            event.preventDefault();

            event.stopPropagation();

            event.stopImmediatePropagation();


            analyzeCurrentPrompt();
        }

    },
    true
);


// ============================================================
// SEND BUTTON INTERCEPTION
// ============================================================

document.addEventListener(
    "click",
    event => {

        // ----------------------------------------------------
        // IMPORTANT:
        // If ShadowShield itself intentionally triggered the
        // send button, let ChatGPT receive that click.
        // ----------------------------------------------------

        if (allowNextSend) {

            console.log(
                "ShadowShield: Allowing approved send click."
            );

            return;
        }


        const button =
            event.target.closest(
                "button"
            );


        if (!button) {
            return;
        }


        const label =
            (
                button.getAttribute(
                    "aria-label"
                ) || ""
            ).toLowerCase();


        const testId =
            button.getAttribute(
                "data-testid"
            ) || "";


        const isSendButton =
            label.includes("send")
            ||
            testId === "send-button";


        if (!isSendButton) {
            return;
        }


        const editor =
            findPromptBox();


        if (!editor) {
            return;
        }


        const text =
            getPromptText(editor);


        if (!text) {
            return;
        }


        console.log(
            "ShadowShield: Send button intercepted."
        );


        event.preventDefault();

        event.stopPropagation();

        event.stopImmediatePropagation();


        analyzeCurrentPrompt();

    },
    true
);