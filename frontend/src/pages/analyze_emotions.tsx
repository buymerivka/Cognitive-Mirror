import React, { useState, useRef } from "react";
import { fetchAnalyzeEmotions } from "../api/client.ts";
import type { SubmitRequest, SingleAnalyze } from "../api/client.ts";
import Header from "../components/Header";
import Footer from "../components/Footer";
import styles from "./analyze_emotions.module.css";
import TextareaAutosize from 'react-textarea-autosize';

const MAX_CHAR = 2048;

const emotionColors: Record<string, string> = {
    'admiration': '#ffd6d6',        // Soft light red
    'amusement': '#ffffd1',         // Very pale yellow
    'anger': '#ffb3ba',             // Pastel red
    'annoyance': '#ffccb8',         // Light coral
    'approval': '#d6ffe0',          // Pale mint
    'caring': '#ffe6cc',            // Light peach
    'confusion': '#e6e6ff',         // Very pale lavender
    'curiosity': '#d6f5ff',         // Pale sky blue
    'desire': '#ffcce6',            // Pastel pink
    'disappointment': '#e6cfe6',    // Light lilac
    'disapproval': '#d9a6a6',       // Muted maroon
    'disgust': '#d9bda6',           // Soft brown
    'embarrassment': '#ffe0e0',     // Pale pink
    'excitement': '#fff5b3',        // Soft yellow
    'fear': '#d6b3e6',              // Light purple
    'gratitude': '#e0ffe6',         // Very pale mint
    'grief': '#cccccc',             // Medium gray
    'joy': '#ffecb3',               // Soft gold
    'love': '#ffb3d9',              // Pastel pink
    'nervousness': '#ffd9b3',       // Soft orange
    'optimism': '#e6ffd6',          // Pastel green
    'pride': '#b3c6ff',             // Light blue
    'realization': '#ccffff',       // Pale aqua
    'relief': '#e6ffe0',            // Very pale green
    'remorse': '#e6b3b3',           // Soft red
    'sadness': '#b3b3ff',           // Light blue
    'surprise': '#f5b3ff',          // Soft pink
    'neutral': '#ffffff',           // White
};

const AnalyzeEmotions: React.FC = () => {
    const [input_data, setText] = useState("");
    const [analyzedData, setAnalyzedData] = useState<SingleAnalyze["analyzed_data"] | null>(null);
    const [loading, setLoading] = useState(false);
    const [selectedEmotions, setSelectedEmotions] = useState<Record<string, boolean>>(
        Object.fromEntries(Object.keys(emotionColors).map((e) => [e, true]))
    );

    const textareaRef = useRef<HTMLTextAreaElement | null>(null);

    const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const el = e.target;
        if (el.value.length > MAX_CHAR) {
            el.value = el.value.slice(0, MAX_CHAR);
        }
        // el.style.height = "auto";
        el.style.height = `${el.scrollHeight}px`;
        setText(el.value);
    };

    const handleAnalyze = async () => {
        if (!input_data.trim()) {
            alert("Please provide a text for emotion analysis.");
            return;
        }
        setLoading(true);
        try {
            const payload: SubmitRequest = { input_data };
            const response: SingleAnalyze = await fetchAnalyzeEmotions(payload);
            setAnalyzedData(response.analyzed_data);
            window.scrollTo({ top: 0, behavior: "smooth" });
        } catch (err) {
            alert("Failed to analyze text");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setText("");
        setAnalyzedData(null);
        setSelectedEmotions(
            Object.fromEntries(Object.keys(emotionColors).map((e) => [e, true]))
        );
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
        }
    };

    const toggleEmotion = (emotion: string) => {
        setSelectedEmotions((prev) => ({ ...prev, [emotion]: !prev[emotion] }));
    };

    const handleDownloadJson = () => {
        if (!analyzedData) return;
        const blob = new Blob([JSON.stringify(analyzedData, null, 2)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "emotion_analysis.json";
        a.click();
        URL.revokeObjectURL(url);
    };

    const renderText = () => {
        if (!analyzedData) return null;
        let isLastInParagraph = false;
        return analyzedData.map((data, idx) => {
            isLastInParagraph = false;
            if (idx < analyzedData.length - 1 && analyzedData[idx + 1].paragraphIndex !== data.paragraphIndex) {
                isLastInParagraph = true;
            }
            const predictions = data.predictions;
            const label = predictions?.[0]?.label || "neutral";
            const color =
                selectedEmotions[label] && label !== "neutral"
                    ? emotionColors[label] || "#ccc"
                    : emotionColors["neutral"];

            if (label !== "neutral" && selectedEmotions[label]) {
                const tooltip = (
                    <div className={styles.tooltiptext}>
                        {predictions?.length === 1 ? (
                            <p>
                                The most likely emotion expressed - <b>{label}</b>, with a probability of
                                <b> {Math.round(predictions[0].score * 10000) / 100}%</b>.
                            </p>
                        ) : (
                            <>
                                <p>
                                    <b>Most likely emotions:</b>
                                </p>
                                <table>
                                    <tbody>
                                    {predictions
                                        ?.filter((p) => selectedEmotions[p.label])
                                        .map((p) => (
                                            <tr key={p.label}>
                                                <td>{p.label}</td>
                                                <td>{Math.round(p.score * 100)}%</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </>
                        )}
                    </div>
                );
                return (
                    <React.Fragment key={idx}>
                        <span
                            className={styles.tooltip}
                            style={{ backgroundColor: color }}
                        >
                        {data.text}
                        {tooltip}
                        {isLastInParagraph && <br/>}
                    </span>{" "}
                        </React.Fragment>
                );
            } else {
                return (
                    <React.Fragment key={idx}>
                        <span
                            // className={styles.tooltip}
                            // style={{ backgroundColor: color }}
                        >
                        {data.text}
                        {isLastInParagraph && <br/>}
                </span>{" "}
                    </React.Fragment>
                );
            }
        });
    };

    return (
        <div className={styles.page}>
            <Header />

            <div className={styles.container}>
                {analyzedData && (
                    <div className={styles.result}>
                        <div className={styles.textResult}>{renderText()}</div>
                        <div className={styles.resultButtons}>
                            <button style={{marginRight: "20px", width: "210px", backgroundColor: "#4caf50"}}
                                    onClick={handleDownloadJson}>Download JSON
                            </button>
                            <button style={{width: "210px"}} onClick={handleClear}>Clear</button>
                        </div>
                    </div>
                )}

                <p className={styles.title}>
                    Provide a text for <b>Emotion Analysis</b>:
                </p>

                <TextareaAutosize
                    className={styles.textarea}
                    value={input_data}
                    onChange={handleTextChange}
                    placeholder="Enter your text here..."
                    ref={textareaRef}
                />

                <div className={styles.actions}>
                    <div className="dropdown">
                        <button
                            className={`${styles.filtersButton} btn btn-secondary dropdown-toggle`}
                            type="button"
                            data-bs-toggle="dropdown"
                            data-bs-auto-close="outside"
                            aria-expanded="false"
                        >
                            Filters
                        </button>

                        <ul className={`${ styles.dropdownMenu } dropdown-menu p-3`} style={{ minWidth: "200px" }}>
                            <p style={{textAlign: "center", marginTop: "16px", fontSize: "18px"}}><b>Show emotions expressed:</b></p>
                            <hr />
                            {Object.keys(selectedEmotions)
                                .filter((e) => e !== "neutral")
                                .map((emotion) => (
                                    <li key={emotion} className="dropdown-item">
                                        <label className={styles.checkboxLabel}>
                                            <input style={{borderColor: "#2c2c2c"}}
                                                type="checkbox"
                                                checked={selectedEmotions[emotion]}
                                                onChange={() => toggleEmotion(emotion)}
                                                className={ `${ styles.formCheckInput } form-check-input me-2` }
                                            />
                                            {emotion.slice(0,1).toUpperCase() + emotion.slice(1, emotion.length)}
                                        </label>
                                    </li>
                                ))}
                        </ul>
                    </div>

                    <div className={styles.charCounter}>
                        {input_data.length} / {MAX_CHAR} characters
                    </div>

                    <button className={`${styles.sendRequestButton} btn btn-secondary`} onClick={handleAnalyze} disabled={loading}>
                        {loading ? "Analyzing..." : "Send a request"}
                    </button>
                </div>
            </div>
            <Footer/>
        </div>
    );
};

export default AnalyzeEmotions;
