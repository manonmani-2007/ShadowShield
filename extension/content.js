console.log("ShadowShield multi-AI content script loaded.");

let shadowShieldChecking = false;
let allowNextSend = false;

// Stores large text captured during paste.
// Claude may convert large pasted content into a "PASTED" card,
// so the editor itself may no longer contain the actual text.
let lastPastedText = "";
let lastPastedTime = 0;


// ============================================================
// PLATFORM DETECTION
// ============================================================

function getPlatform() {

    const host = window.location.hostname;

    if (
        host === "chatgpt.com" ||
        host === "chat.openai.com"
    ) {
        return "chatgpt";
    }

    if (host === "gemini.google.com") {
        return "gemini";
    }

    if (
        host === "claude.ai" ||
        host.endsWith(".claude.ai")
    ) {
        return "claude";
    }

    return "generic";
}


// ============================================================
// FIND PROMPT BOX
// ============================================================

function findPromptBox() {

    const platform = getPlatform();

    // --------------------------------------------------------
    // CLAUDE
    // --------------------------------------------------------

    if (platform === "claude") {

        const claudeEditor =
            document.querySelector(
                'div[contenteditable="true"].tiptap.ProseMirror[aria-label="Write your prompt to Claude"]'
            );

        if (claudeEditor) {
            return claudeEditor;
        }

        const claudeFallback =
            document.querySelector(
                'div[contenteditable="true"].tiptap.ProseMirror'
            );

        if (claudeFallback) {
            return claudeFallback;
        }
    }


    // --------------------------------------------------------
    // CHATGPT
    // --------------------------------------------------------

    if (platform === "chatgpt") {

        const chatgptEditor =
            document.querySelector(
                "div[contenteditable='true'].ProseMirror"
            );

        if (chatgptEditor) {
            return chatgptEditor;
        }
    }


    // --------------------------------------------------------
    // GEMINI
    // --------------------------------------------------------

    if (platform === "gemini") {

        const geminiEditor =
            document.querySelector(
                'div[contenteditable="true"]'
            );

        if (geminiEditor) {
            return geminiEditor;
        }

        const textarea =
            document.querySelector("textarea");

        if (textarea) {
            return textarea;
        }
    }


    // --------------------------------------------------------
    // GENERIC
    // --------------------------------------------------------

    return (
        document.querySelector(
            'div[contenteditable="true"]'
        ) ||
        document.querySelector("textarea")
    );
}


// ============================================================
// GET EDITOR TEXT
// ============================================================

function getEditorText(editor) {

    if (!editor) {
        return "";
    }

    if (
        editor.tagName === "TEXTAREA" ||
        editor.tagName === "INPUT"
    ) {
        return (editor.value || "").trim();
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

function getCurrentPrompt() {

    const editor = findPromptBox();

    if (!editor) {
        return "";
    }

    const editorText =
        getEditorText(editor);

    // --------------------------------------------------------
    // CLAUDE LARGE PASTE HANDLING
    // --------------------------------------------------------
    //
    // Claude may transform a large paste into a PASTED card.
    // In that case editorText may be only 1-2 lines.
    //
    // If we recently captured a substantial clipboard paste,
    // use the captured text instead.
    // --------------------------------------------------------

    if (getPlatform() === "claude") {

        const pasteAge =
            Date.now() - lastPastedTime;

        const hasRecentPaste =
            lastPastedText &&
            pasteAge < 5 * 60 * 1000;

        if (
            hasRecentPaste &&
            lastPastedText.length > editorText.length * 3 &&
            lastPastedText.length > 200
        ) {

            console.log(
                "ShadowShield: Using captured Claude paste.",
                {
                    editorCharacters: editorText.length,
                    capturedCharacters: lastPastedText.length
                }
            );

            return lastPastedText;
        }
    }

    return editorText;
}


// ============================================================
// CAPTURE PASTE
// ============================================================

document.addEventListener(
    "paste",
    event => {

        const platform =
            getPlatform();

        if (
            platform !== "claude"
        ) {
            return;
        }

        const target =
            event.target;

        if (
            !target ||
            !target.closest
        ) {
            return;
        }

        const editor =
            target.closest(
                'div[contenteditable="true"]'
            );

        if (!editor) {
            return;
        }

        let pastedText = "";

        // ClipboardEvent clipboardData
        if (
            event.clipboardData &&
            event.clipboardData.getData
        ) {

            pastedText =
                event.clipboardData.getData(
                    "text/plain"
                );
        }

        // Fallback
        if (!pastedText) {

            try {

                pastedText =
                    event.clipboardData.getData(
                        "text"
                    );

            } catch (error) {
                console.warn(
                    "ShadowShield: Could not read pasted text.",
                    error
                );
            }
        }

        if (
            pastedText &&
            pastedText.trim()
        ) {

            lastPastedText =
                pastedText;

            lastPastedTime =
                Date.now();

            console.log(
                "ShadowShield: Captured Claude paste.",
                {
                    characters:
                        pastedText.length,

                    lines:
                        pastedText.split("\n").length
                }
            );
        }

    },
    true
);


// ============================================================
// SEND TO FASTAPI
// ============================================================

function sendForAnalysis(text) {

    return new Promise(resolve => {

        try {

            chrome.runtime.sendMessage(
                {
                    type: "ANALYZE_PROMPT",
                    text: text
                },
                response => {

                    if (
                        chrome.runtime.lastError
                    ) {

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

        } catch (error) {

            console.error(
                "ShadowShield message error:",
                error
            );

            resolve(null);
        }
    });
}


// ============================================================
// FIND SEND BUTTON
// ============================================================

function findSendButton() {

    const platform =
        getPlatform();


    // --------------------------------------------------------
    // CLAUDE
    // --------------------------------------------------------

    if (
        platform === "claude"
    ) {

        const button =
            document.querySelector(
                'button[aria-label="Send message"]'
            );

        if (
            button &&
            !button.disabled
        ) {
            return button;
        }
    }


    // --------------------------------------------------------
    // CHATGPT
    // --------------------------------------------------------

    if (
        platform === "chatgpt"
    ) {

        const button =
            document.querySelector(
                "button[data-testid='send-button']"
            );

        if (
            button &&
            !button.disabled
        ) {
            return button;
        }
    }


    // --------------------------------------------------------
    // GEMINI
    // --------------------------------------------------------

    if (
        platform === "gemini"
    ) {

        const buttons =
            document.querySelectorAll(
                "button"
            );

        for (
            const button of buttons
        ) {

            if (button.disabled) {
                continue;
            }

            const aria =
                (
                    button.getAttribute(
                        "aria-label"
                    ) || ""
                ).toLowerCase();

            const title =
                (
                    button.getAttribute(
                        "title"
                    ) || ""
                ).toLowerCase();

            const text =
                (
                    button.innerText ||
                    ""
                ).toLowerCase();

            if (
                aria.includes("send") ||
                aria.includes("submit") ||
                title.includes("send") ||
                title.includes("submit") ||
                text === "send"
            ) {
                return button;
            }
        }
    }


    // --------------------------------------------------------
    // GENERIC
    // --------------------------------------------------------

    const buttons =
        document.querySelectorAll(
            "button"
        );

    for (
        const button of buttons
    ) {

        if (button.disabled) {
            continue;
        }

        const aria =
            (
                button.getAttribute(
                    "aria-label"
                ) || ""
            ).toLowerCase();

        const title =
            (
                button.getAttribute(
                    "title"
                ) || ""
            ).toLowerCase();

        const text =
            (
                button.innerText ||
                ""
            ).toLowerCase();

        if (
            aria.includes("send") ||
            title.includes("send") ||
            text === "send"
        ) {
            return button;
        }
    }

    return null;
}


// ============================================================
// REPLACE TEXTAREA
// ============================================================

function replaceTextareaText(
    editor,
    newText
) {

    try {

        editor.focus();

        const prototype =
            Object.getPrototypeOf(
                editor
            );

        const descriptor =
            Object.getOwnPropertyDescriptor(
                prototype,
                "value"
            );

        if (
            descriptor &&
            descriptor.set
        ) {

            descriptor.set.call(
                editor,
                newText
            );

        } else {

            editor.value =
                newText;
        }

        editor.dispatchEvent(
            new Event(
                "input",
                {
                    bubbles: true
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

    } catch (error) {

        console.error(
            "ShadowShield textarea replacement failed:",
            error
        );

        return false;
    }
}


// ============================================================
// REPLACE CONTENTEDITABLE
// ============================================================

function replaceContentEditableText(
    editor,
    newText
) {

    if (!editor) {
        return false;
    }

    try {

        editor.focus();


        // Select everything inside the editor.
        const selection =
            window.getSelection();

        const range =
            document.createRange();

        range.selectNodeContents(
            editor
        );

        selection.removeAllRanges();

        selection.addRange(
            range
        );


        let success =
            false;


        // First try execCommand.
        try {

            success =
                document.execCommand(
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


        // Fallback for a normal contenteditable.
        if (!success) {

            editor.textContent =
                newText;
        }


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

    } catch (error) {

        console.error(
            "ShadowShield contenteditable replacement failed:",
            error
        );

        return false;
    }
}


// ============================================================
// REPLACE EDITOR
// ============================================================

function replaceEditorText(
    editor,
    newText
) {

    if (!editor) {
        return false;
    }

    if (
        editor.tagName === "TEXTAREA" ||
        editor.tagName === "INPUT"
    ) {

        return replaceTextareaText(
            editor,
            newText
        );
    }

    return replaceContentEditableText(
        editor,
        newText
    );
}


// ============================================================
// CLICK APPROVED SEND
// ============================================================

function clickPlatformSend() {

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
            "ShadowShield: Send button disabled."
        );

        return false;
    }

    console.log(
        "ShadowShield: Sending approved prompt."
    );

    allowNextSend =
        true;

    setTimeout(
        () => {

            const currentButton =
                findSendButton();

            if (
                currentButton &&
                !currentButton.disabled
            ) {

                currentButton.click();

            } else {

                console.warn(
                    "ShadowShield: Approved send button unavailable."
                );
            }

            setTimeout(
                () => {
                    allowNextSend = false;
                },
                1000
            );

        },
        400
    );

    return true;
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        text || "";

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
        document.createElement(
            "div"
        );

    overlay.id =
        "shadowshield-warning";


    overlay.addEventListener(
        "click",
        event => {
            event.stopPropagation();
        }
    );


    const detections =
        Array.isArray(
            result.detections
        )
            ? result.detections
            : [];


    const detectionList =
        detections
            .map(
                detection => {

                    const type =
                        detection.type ||
                        "sensitive information";

                    return `
                        <div>
                            • ${escapeHtml(type)}
                        </div>
                    `;
                }
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
                        result.risk_level ||
                        "SENSITIVE"
                    )}
                </strong>

                <br>

                Risk Score:
                <strong>
                    ${escapeHtml(
                        String(
                            result.risk_score ??
                            "N/A"
                        )
                    )}
                </strong>

            </div>

            <div class="shadowshield-detections">

                <strong>
                    Detected information:
                </strong>

                ${detectionList}

            </div>

            <div class="shadowshield-preview">

                <strong>
                    Redacted version:
                </strong>

                <div class="shadowshield-text">
                    ${escapeHtml(
                        result.redacted_text ||
                        ""
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


    // --------------------------------------------------------
    // REDACT & SEND
    // --------------------------------------------------------

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


                const replacement =
                    result.redacted_text ||
                    "";


                const replaced =
                    replaceEditorText(
                        editor,
                        replacement
                    );


                if (!replaced) {

                    console.error(
                        "ShadowShield: Could not replace editor."
                    );

                    return;
                }


                // Clear the captured original
                // so it cannot be reused accidentally.
                lastPastedText = "";
                lastPastedTime = 0;


                removeWarning();


                setTimeout(
                    () => {
                        clickPlatformSend();
                    },
                    500
                );
            }
        );


    // --------------------------------------------------------
    // EDIT
    // --------------------------------------------------------

    document
        .getElementById(
            "shadowshield-edit"
        )
        .addEventListener(
            "click",
            event => {

                event.preventDefault();
                event.stopPropagation();

                removeWarning();

                setTimeout(
                    () => {

                        const currentEditor =
                            findPromptBox();

                        if (currentEditor) {
                            currentEditor.focus();
                        }

                    },
                    100
                );
            }
        );


    // --------------------------------------------------------
    // SEND ANYWAY
    // --------------------------------------------------------

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


                lastPastedText = "";
                lastPastedTime = 0;


                removeWarning();


                setTimeout(
                    () => {
                        clickPlatformSend();
                    },
                    200
                );
            }
        );


    // --------------------------------------------------------
    // CANCEL
    // --------------------------------------------------------

    document
        .getElementById(
            "shadowshield-cancel"
        )
        .addEventListener(
            "click",
            event => {

                event.preventDefault();
                event.stopPropagation();

                removeWarning();
            }
        );
}


// ============================================================
// ANALYZE CURRENT PROMPT
// ============================================================

async function analyzeCurrentPrompt() {

    if (shadowShieldChecking) {
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
        getCurrentPrompt();


    if (!text) {

        console.warn(
            "ShadowShield: Empty prompt."
        );

        return;
    }


    shadowShieldChecking =
        true;


    console.log(
        "ShadowShield: Analyzing prompt..."
    );


    console.log(
        "ShadowShield: Prompt size:",
        {
            characters: text.length,
            lines: text.split("\n").length
        }
    );


    const response =
        await sendForAnalysis(
            text
        );


    shadowShieldChecking =
        false;


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
        "ShadowShield analysis:",
        result
    );


    // --------------------------------------------------------
    // SAFE
    // --------------------------------------------------------

    if (
        result.risk_level === "SAFE"
    ) {

        console.log(
            "ShadowShield: SAFE → allowing submission."
        );

        lastPastedText = "";
        lastPastedTime = 0;

        clickPlatformSend();

        return;
    }


    // --------------------------------------------------------
    // SENSITIVE / HIGH RISK
    // --------------------------------------------------------

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
            event.key !== "Enter" ||
            event.shiftKey
        ) {
            return;
        }


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


        if (
            event.target !== editor &&
            !editor.contains(
                event.target
            )
        ) {
            return;
        }


        const text =
            getCurrentPrompt();


        if (!text) {
            return;
        }


        console.log(
            "ShadowShield: Enter intercepted on",
            getPlatform()
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

        // ----------------------------------------------------
        // APPROVED SEND
        // ----------------------------------------------------

        if (allowNextSend) {
            return;
        }


        // ----------------------------------------------------
        // IGNORE SHADOWSHIELD DIALOG
        // ----------------------------------------------------

        if (
            event.target.closest &&
            event.target.closest(
                "#shadowshield-warning"
            )
        ) {
            return;
        }


        const button =
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


        const title =
            (
                button.getAttribute(
                    "title"
                ) || ""
            ).toLowerCase();


        const text =
            (
                button.innerText ||
                ""
            ).trim().toLowerCase();


        const testId =
            button.getAttribute(
                "data-testid"
            ) || "";


        let isSendButton =
            false;


        // Claude
        if (
            platform === "claude" &&
            label === "send message"
        ) {
            isSendButton = true;
        }


        // ChatGPT
        if (
            platform === "chatgpt" &&
            (
                testId === "send-button" ||
                label.includes("send")
            )
        ) {
            isSendButton = true;
        }


        // Gemini
        if (
            platform === "gemini" ||
            platform === "generic"
        ) {

            if (
                label.includes("send") ||
                label.includes("submit") ||
                title.includes("send") ||
                title.includes("submit") ||
                text === "send"
            ) {
                isSendButton = true;
            }
        }


        if (!isSendButton) {
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


        const promptText =
            getCurrentPrompt();


        if (!promptText) {

            console.warn(
                "ShadowShield: Prompt text empty."
            );

            return;
        }


        console.log(
            "ShadowShield: Send button intercepted on",
            platform
        );


        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();


        analyzeCurrentPrompt();

    },
    true
);


// ============================================================
// STATUS
// ============================================================

console.log(
    "ShadowShield platform:",
    getPlatform()
);