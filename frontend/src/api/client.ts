const API_URL = "http://127.0.0.1:8000";

export interface SingleAnalyze {
    analyzed_data: [];
}

export interface SubmitRequest {
    text: string;
}

async function fetchAnalyze(data: SubmitRequest): Promise<SingleAnalyze> {
    const res = await fetch(`${API_URL}/analyze_emotions`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({data})
    });

    if (!res.ok) throw new Error("Failed to analyze data");
    return res.json();
}