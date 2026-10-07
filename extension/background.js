const API_URL = "https://shadowshield-5zyf.onrender.com/analyze";

chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (message.type !== "ANALYZE_PROMPT") {
            return;
        }

        fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: message.text
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`API returned ${response.status}`);
            }

            return response.json();
        })
        .then(data => {
            sendResponse({
                success: true,
                data: data
            });
        })
        .catch(error => {
            console.error("ShadowShield API error:", error);

            sendResponse({
                success: false,
                error: error.message
            });
        });

        return true;
    }
);