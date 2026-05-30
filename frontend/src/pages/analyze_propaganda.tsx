import React, { useState, useRef } from "react";
import { fetchAnalyzePropaganda } from "../api/client.ts";
import type { SubmitRequest, SingleAnalyze } from "../api/client.ts";
import Header from "../components/Header";
import Footer from "../components/Footer";
import styles from "./analyze_propaganda.module.css";
import TextareaAutosize from 'react-textarea-autosize';


const MAX_CHAR = 2048;

const PropagandaColors: Record<string, string> = {
    'LABEL_0': '#ffffff',      // White
    'LABEL_1': '#cd5c5c',      // Indian red
};

const AnalyzePropaganda: React.FC = () => {
    const [input_data, setText] = useState("");
    const [analyzedData, setAnalyzedData] = useState<SingleAnalyze["analyzed_data"] | null>(null);
    const [loading, setLoading] = useState(false);

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
            alert("Please provide a text for manipulation analysis.");
            return;
        }
        setLoading(true);
        try {
            const payload: SubmitRequest = { input_data };
            const response: SingleAnalyze = await fetchAnalyzePropaganda(payload);
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
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
        }
    };

    const handleDownloadJson = () => {
        if (!analyzedData) return;
        const blob = new Blob([JSON.stringify(analyzedData, null, 2)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "propaganda_analysis.json";
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
            const label = predictions?.[0]?.label || "none";
            const color =
                label !== "none"
                    ? PropagandaColors[label] || "#ccc"
                    : PropagandaColors["none"];

            if (label !== "none") {
                const tooltip = (
                    <div className={styles.tooltiptext}>
                        {predictions?.length === 1 ? (
                            <p>
                                This is most likely a <b>propagandistic</b> sentence, with a probability of
                                <b> {Math.round(predictions[0].score * 10000) / 100}%</b>.
                            </p>
                        ) : (
                            <>
                                <p>
                                    <b>Most likely propaganda:</b>
                                </p>
                                <table>
                                    <tbody>
                                    {predictions.map((p) => (
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
                    Provide a text for <b>Propaganda Analysis</b>:
                </p>

                <TextareaAutosize
                    className={styles.textarea}
                    value={input_data}
                    onChange={handleTextChange}
                    placeholder="Enter your text here..."
                    ref={textareaRef}
                />

                <div className={styles.actions}>
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

export default AnalyzePropaganda;
