const API_URL = "http://127.0.0.1:8000";

export interface SingleAnalyze {
    analyzed_data: AnalyzedText[];
}

export interface DualAnalyze {
    manipulations_analyzed: AnalyzedText[];
    emotions_analyzed: AnalyzedText[];
}

export interface FullAnalyze {
    propaganda_analyzed: AnalyzedText[];
    manipulations_analyzed: AnalyzedText[];
    emotions_analyzed: AnalyzedText[];
}

export interface SubmitRequest {
    input_data: string;
}

export interface Prediction {
    label: string;
    score: number;
}

export interface AnalyzedText {
    text: string;
    predictions: Prediction[];
    paragraphIndex: number;
}


export async function fetchAnalyzeEmotions(data: SubmitRequest): Promise<SingleAnalyze> {
    const res = await fetch(`${API_URL}/analyze_emotions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to analyze data");
    return res.json();
}

export async function fetchAnalyzeManipulations(data: SubmitRequest): Promise<SingleAnalyze> {
    const res = await fetch(`${API_URL}/analyze_manipulations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to analyze data");
    return res.json();
}

export async function fetchAnalyzePropaganda(data: SubmitRequest): Promise<SingleAnalyze> {
    const res = await fetch(`${API_URL}/analyze_propaganda`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to analyze data");
    return res.json();
}

export async function fetchAnalyzeManipulationsAndEmotions(data: SubmitRequest): Promise<DualAnalyze> {
    const res = await fetch(`${API_URL}/analyze_manipulations_and_emotions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to analyze data");
    return res.json();
}

export async function fetchAnalyze(data: SubmitRequest): Promise<FullAnalyze> {
    const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to analyze data");
    return res.json();
}
