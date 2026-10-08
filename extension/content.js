// ============================================================
// SHADOWSHIELD CONTENT SCRIPT
// ChatGPT + Gemini + Claude
// ============================================================

console.log("ShadowShield: Content script loaded.");

let shadowShieldChecking = false;
let allowNextSend = false;

// Claude can convert a large clipboard paste into a "PASTED"
// object/card. We preserve the original clipboard text here.
let lastPastedText = "";
let lastPastedTime = 0;


// ============================================================
// PLATFORM DETECTION
// ============================================================

function getPlatform() {

    const host = window.location.hostname;

    if (
        host.includes("chatgpt.com") ||
        host.includes("chat.openai.com")
    ) {
        return "chatgpt";
    }

    if (host.includes("gemini.google.com")) {
        return "gemini";
    }

    if (host.includes("claude.ai")) {
        return "claude";
    }

    return "unknown";
}


// ============================================================
// FIND PROMPT EDITOR
// ============================================================

function findPromptBox() {

    const platform = getPlatform();

    // --------------------------------------------------------
    // CHATGPT
    // --------------------------------------------------------

    if (platform === "chatgpt") {

        const chatGPTEditor =
            document.querySelector(
                "div[contenteditable='true'].ProseMirror"
            );

        if (chatGPTEditor) {
            return chatGPTEditor;
        }
    }


    // --------------------------------------------------------
    // CLAUDE
    // --------------------------------------------------------

    if (platform === "claude") {

        const claudeEditor =
            document.querySelector(
                "div.tiptap.ProseMirror[contenteditable='true']"
            );

        if (claudeEditor) {
            return claudeEditor;
        }

        const claudeGeneric =
            document.querySelector(
                "div[contenteditable='true'][aria-label*='prompt' i]"
            );

        if (claudeGeneric) {
            return claudeGeneric;
        }
    }


    // --------------------------------------------------------
    // GEMINI
    // --------------------------------------------------------

    if (platform === "gemini") {

        const geminiEditor =
            document.querySelector(
                "div[contenteditable='true']"
            );

        if (geminiEditor) {
            return geminiEditor;
        }
    }


    // --------------------------------------------------------
    // GENERIC FALLBACK
    // --------------------------------------------------------

    return document.querySelector(
        "div[contenteditable='true']"
    );
}


// ============================================================
// GET NORMAL EDITOR TEXT
// ============================================================

function getEditorText(editor) {

    if (!editor) {
        return "";
    }

    return (
        editor.innerText ||
        editor.textContent ||
        ""
    ).trim();
}


// ============================================================
// GET CURRENT PROMPT
// ============================================================

function getCurrentPrompt(editor) {

    const editorText =
        getEditorText(editor);

    const platform =
        getPlatform();

    // --------------------------------------------------------
    // CLAUDE LARGE-PASTE FIX
    // --------------------------------------------------------
    //
    // Claude may turn a large paste into a "PASTED" object.
    // The editor then contains only a small representation
    // instead of the complete clipboard text.
    //
    // If a recent clipboard paste is substantially larger
    // than the editor content, use the original pasted text.
    // --------------------------------------------------------

    if (platform === "claude") {

        const now =
            Date.now();

        const recentPaste =
            (
                lastPastedText &&
                (now - lastPastedTime) < 10000
            );

        if (
            recentPaste &&
            lastPastedText.length > 500 &&
            lastPastedText.length >
                Math.max(
                    editorText.length * 2,
                    1000
                )
        ) {

            console.log(
                "ShadowShield: Using captured Claude paste."
            );

            console.log(
                "ShadowShield: Captured characters:",
                lastPastedText.length
            );

            console.log(
                "ShadowShield: Captured lines:",
                lastPastedText.split(/\r?\n/).length
            );

            return lastPastedText.trim();
        }
    }

    return editorText;
}


// ============================================================
// CAPTURE CLIPBOARD PASTE
// ============================================================

document.addEventListener(
    "paste",
    event => {

        try {

            const pastedText =
                event.clipboardData
                    ?.getData("text/plain");

            if (
                pastedText &&
                pastedText.trim()
            ) {

                lastPastedText =
                    pastedText;

                lastPastedTime =
                    Date.now();

                console.log(
                    "ShadowShield: Paste captured."
                );

                console.log(
                    "ShadowShield: Captured characters:",
                    pastedText.length
                );

                console.log(
                    "ShadowShield: Captured lines:",
                    pastedText.split(/\r?\n/).length
                );
            }

        } catch (error) {

            console.warn(
                "ShadowShield: Could not capture paste:",
                error
            );
        }

    },
    true
);


// ============================================================
// SEND PROMPT TO BACKGROUND SERVICE WORKER
// ============================================================

function sendForAnalysis(text) {

    return new Promise(resolve => {

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

                    resolve({
                        success: false,
                        error:
                            chrome.runtime.lastError.message
                    });

                    return;
                }

                resolve(response);
            }
        );
    });
}


// ============================================================
// FIND SEND BUTTON
// ============================================================

function findSendButton() {

    const platform =
        getPlatform();


    // --------------------------------------------------------
    // CHATGPT
    // --------------------------------------------------------

    if (platform === "chatgpt") {

        const chatGPTButton =
            document.querySelector(
                "button[data-testid='send-button']"
            );

        if (chatGPTButton) {
            return chatGPTButton;
        }
    }


    // --------------------------------------------------------
    // GEMINI
    // --------------------------------------------------------

    if (platform === "gemini") {

        const geminiButton =
            document.querySelector(
                "button[aria-label='Send message']"
            );

        if (geminiButton) {
            return geminiButton;
        }

        const geminiButton2 =
            document.querySelector(
                "button[data-testid='send-button']"
            );

        if (geminiButton2) {
            return geminiButton2;
        }
    }


    // --------------------------------------------------------
    // CLAUDE
    // --------------------------------------------------------

    if (platform === "claude") {

        const claudeButton =
            document.querySelector(
                "button[aria-label='Send message']"
            );

        if (claudeButton) {
            return claudeButton;
        }
    }


    // --------------------------------------------------------
    // GENERIC FALLBACK
    // --------------------------------------------------------

    const buttons =
        document.querySelectorAll("button");

    for (const button of buttons) {

        const label =
            (
                button.getAttribute("aria-label") ||
                ""
            ).toLowerCase();

        const testId =
            button.getAttribute("data-testid") ||
            "";

        if (
            testId === "send-button" ||
            label === "send message" ||
            label.includes("send")
        ) {

            return button;
        }
    }

    return null;
}


// ============================================================
// PROGRAMMATICALLY SEND APPROVED PROMPT
// ============================================================

function clickApprovedSend() {

    const button =
        findSendButton();

    if (!button) {

        console.warn(
            "ShadowShield: Send button not found."
        );

        return false;
    }

    if (button.disabled) {

        console.warn(
            "ShadowShield: Send button is disabled."
        );

        return false;
    }

    console.log(
        "ShadowShield: Sending approved prompt."
    );

    allowNextSend = true;

    setTimeout(() => {

        const currentButton =
            findSendButton();

        if (!currentButton) {

            allowNextSend = false;

            console.warn(
                "ShadowShield: Send button disappeared."
            );

            return;
        }

        if (currentButton.disabled) {

            allowNextSend = false;

            console.warn(
                "ShadowShield: Send button became disabled."
            );

            return;
        }

        currentButton.click();

        setTimeout(() => {

            allowNextSend = false;

        }, 1000);

    }, 300);

    return true;
}


// ============================================================
// REPLACE EDITOR TEXT
// ============================================================

function replaceEditorText(
    editor,
    newText
) {

    if (!editor) {
        return false;
    }

    editor.focus();

    try {

        const selection =
            window.getSelection();

        const range =
            document.createRange();

        range.selectNodeContents(editor);

        selection.removeAllRanges();

        selection.addRange(range);

    } catch (error) {

        console.warn(
            "ShadowShield: Selection error:",
            error
        );
    }


    let success = false;

    try {

        success =
            document.execCommand(
                "insertText",
                false,
                newText
            );

    } catch (error) {

        console.warn(
            "ShadowShield: execCommand failed:",
            error
        );
    }


    // --------------------------------------------------------
    // FALLBACK
    // --------------------------------------------------------

    if (!success) {

        editor.textContent =
            newText;
    }


    // --------------------------------------------------------
    // Notify framework
    // --------------------------------------------------------

    try {

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

    } catch (error) {

        editor.dispatchEvent(
            new Event(
                "input",
                {
                    bubbles: true
                }
            )
        );
    }


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
// HTML ESCAPE
// ============================================================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        String(text ?? "");

    return div.innerHTML;
}


// ============================================================
// REMOVE WARNING
// ============================================================

function removeWarning() {

    const existing =
        document.getElementById(
            "shadowshield-warning"
        );

    if (existing) {
        existing.remove();

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

    removeWarning();


    const overlay =
        document.createElement("div");

    overlay.id =
        "shadowshield-warning";


    // Prevent clicks inside our UI from reaching
    // the AI platform's click handler.
    overlay.addEventListener(
        "click",
        event => {

            event.stopPropagation();

        }
    );


    const detections =
        Array.isArray(result.detections)
            ? result.detections
            : [];


    const detectionList =
        detections.length > 0

            ? detections
                .map(
                    detection => `
                        <div>
                            • ${escapeHtml(
                                detection.type
                            )}
                        </div>
                    `
                )
                .join("")

            : `
                <div>
                    • Sensitive information detected
                </div>
            `;


    const redactedText =
        result.redacted_text ||
        "";


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
                        result.risk_level ||
                        "UNKNOWN"
                    )}
                </strong>
            </div>

            <div class="shadowshield-risk">
                Risk Score:
                <strong>
                    ${escapeHtml(
                        result.risk_score ??
                        "N/A"
                    )}
                </strong>
            </div>

            <div class="shadowshield-risk">
                Findings:
                <strong>
                    ${escapeHtml(
                        result.total_findings ??
                        detections.length
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
                        redactedText
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


                const replaced =
                    replaceEditorText(
                        editor,
                        redactedText
                    );


                if (!replaced) {

                    console.error(
                        "ShadowShield: Could not update editor."
                    );

                    return;
                }


                removeWarning();


                setTimeout(() => {

                    clickApprovedSend();

                }, 500);

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

                    clickApprovedSend();

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

                removeWarning();

            }
        );
}


// ============================================================
// ANALYZE CURRENT PROMPT
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
        getCurrentPrompt(editor);


    if (!text) {
        return;
    }


    shadowShieldChecking = true;


    console.log(
        "ShadowShield: Analyzing prompt..."
    );

    console.log(
        "ShadowShield: Prompt size:",
        {
            characters: text.length,
            lines:
                text.split(/\r?\n/).length
        }
    );


    const response =
        await sendForAnalysis(text);


    shadowShieldChecking = false;


    if (
        !response ||
        !response.success
    ) {

        console.error(
            "ShadowShield: Analysis failed.",
            response
        );

        return;
    }


    const result =
        response.data;


    console.log(
        "ShadowShield: Analysis result:",
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

        clickApprovedSend();

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
// ENTER KEY INTERCEPTION
// ============================================================

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key !== "Enter" ||
            event.shiftKey
        ) {
            return;
        }


        // Ignore if a warning button is focused.
        if (
            event.target.closest &&
            event.target.closest(
                "#shadowshield-warning"
            )
        ) {
            return;
        }


        const editor =
            findPromptBox();


        if (!editor) {
            return;
        }


        // Only intercept when the active element
        // is actually the prompt editor.
        if (
            document.activeElement !== editor &&
            !editor.contains(
                document.activeElement
            )
        ) {
            return;
        }


        const text =
            getCurrentPrompt(editor);


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

    },
    true
);


// ============================================================
// SEND BUTTON INTERCEPTION
// ============================================================

document.addEventListener(
    "click",
    event => {

        // Allow a send that ShadowShield intentionally
        // triggered after approval.
        if (allowNextSend) {

            console.log(
                "ShadowShield: Allowing approved send click."
            );

            return;
        }


        // Ignore ShadowShield's own warning buttons.
        if (
            event.target.closest &&
            event.target.closest(
                "#shadowshield-warning"
            )
        ) {
            return;
        }


        const button =
            event.target.closest &&
            event.target.closest(
                "button"
            );


        if (!button) {
            return;
        }


        const platform =
            getPlatform();


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


        let isSendButton = false;


        // ----------------------------------------------------
        // CHATGPT
        // ----------------------------------------------------

        if (
            platform === "chatgpt" &&
            (
                testId === "send-button" ||
                label.includes("send")
            )
        ) {
            isSendButton = true;
        }


        // ----------------------------------------------------
        // GEMINI
        // ----------------------------------------------------

        if (
            platform === "gemini" &&
            (
                label === "send message" ||
                label.includes("send")
            )
        ) {
            isSendButton = true;
        }


        // ----------------------------------------------------
        // CLAUDE
        // ----------------------------------------------------

        if (
            platform === "claude" &&
            (
                label === "send message" ||
                label.includes("send")
            )
        ) {
            isSendButton = true;
        }


        // Generic fallback
        if (
            !isSendButton &&
            (
                testId === "send-button" ||
                label === "send message"
            )
        ) {
            isSendButton = true;
        }


        if (!isSendButton) {
            return;
        }


        const editor =
            findPromptBox();


        if (!editor) {
            return;
        }


        const text =
            getCurrentPrompt(editor);


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


// ============================================================
// PAGE LOAD MESSAGE
// ============================================================

console.log(
    "ShadowShield: Platform =",
    getPlatform()
);