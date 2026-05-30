import React, { useState, useRef } from "react";
import { fetchAnalyzeManipulations } from "../api/client.ts";
import type { SubmitRequest, SingleAnalyze } from "../api/client.ts";
import Header from "../components/Header";
import Footer from "../components/Footer";
import styles from "./analyze_manipulations.module.css";
import TextareaAutosize from 'react-textarea-autosize';

const MAX_CHAR = 2048;

const manipulationsColors: Record<string, string> = {
    'none': '#ffffff',                      // White
    'false dilemma': '#b0c4de',             // Light steel blue
    'slippery slope': '#cdb79e',            // Warm beige
    'appeal to nature': '#b2d8b2',          // Soft green
    'appeal to authority': '#c0b7dd',       // Light lavender
    'appeal to majority': '#f0d9b5',        // Pale almond
    'hasty generalization': '#e6ccb2',      // Muted peach
    'appeal to worse problems': '#c2d6d6',  // Desaturated teal
    'appeal to tradition': '#deb887',       // Burlywood
};

const AnalyzeManipulations: React.FC = () => {
    const [input_data, setText] = useState("");
    const [analyzedData, setAnalyzedData] = useState<SingleAnalyze["analyzed_data"] | null>(null);
    const [loading, setLoading] = useState(false);
    const [selectedManipulations, setSelectedManipulations] = useState<Record<string, boolean>>(
        Object.fromEntries(Object.keys(manipulationsColors).map((e) => [e, true]))
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
            alert("Please provide a text for manipulation analysis.");
            return;
        }
        setLoading(true);
        try {
            const payload: SubmitRequest = { input_data };
            const response: SingleAnalyze = await fetchAnalyzeManipulations(payload);
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
        setSelectedManipulations(
            Object.fromEntries(Object.keys(manipulationsColors).map((e) => [e, true]))
        );
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
        }
    };

    const toggleManipulation = (manipulation: string) => {
        setSelectedManipulations((prev) => ({ ...prev, [manipulation]: !prev[manipulation] }));
    };

    const handleDownloadJson = () => {
        if (!analyzedData) return;
        const blob = new Blob([JSON.stringify(analyzedData, null, 2)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "manipulation_analysis.json";
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
                selectedManipulations[label] && label !== "none"
                    ? manipulationsColors[label] || "#ccc"
                    : manipulationsColors["none"];

            if (label !== "none" && selectedManipulations[label]) {
                const tooltip = (
                    <div className={styles.tooltiptext}>
                        {predictions?.length === 1 ? (
                            <p>
                                The most likely manipulation technique used - <b>{label}</b>, with a probability of
                                <b> {Math.round(predictions[0].score * 10000) / 100}%</b>.
                            </p>
                        ) : (
                            <>
                                <p>
                                    <b>Most likely manipulations:</b>
                                </p>
                                <table>
                                    <tbody>
                                    {predictions
                                        ?.filter((p) => selectedManipulations[p.label])
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
                    Provide a text for <b>Manipulation Analysis</b>:
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
                            <p style={{textAlign: "center", marginTop: "16px", fontSize: "18px"}}><b>Show manipulation techniques:</b></p>
                            <hr />
                            {Object.keys(selectedManipulations)
                                .filter((e) => e !== "none")
                                .map((manipulation) => (
                                    <li key={manipulation} className="dropdown-item">
                                        <label className={styles.checkboxLabel}>
                                            <input style={{borderColor: "#2c2c2c"}}
                                                type="checkbox"
                                                checked={selectedManipulations[manipulation]}
                                                onChange={() => toggleManipulation(manipulation)}
                                                className={ `${ styles.formCheckInput } form-check-input me-2` }
                                            />
                                            {manipulation.slice(0,1).toUpperCase() + manipulation.slice(1, manipulation.length)}
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

export default AnalyzeManipulations;
