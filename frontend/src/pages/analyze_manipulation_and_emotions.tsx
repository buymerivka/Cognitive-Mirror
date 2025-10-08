import React, { useState, useRef } from "react";
import {fetchAnalyzeManipulationsAndEmotions} from "../api/client.ts";
import type { SubmitRequest, DualAnalyze } from "../api/client.ts";
import Header from "../components/Header";
import Footer from "../components/Footer";
import styles from "./analyze_manipulation_and_emotion.module.css";
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
    const [analyzedData, setAnalyzedData] = useState<{
        manipulations_analyzed: DualAnalyze["manipulations_analyzed"];
        emotions_analyzed: DualAnalyze["emotions_analyzed"];
    } | null>(null);
    const [loading, setLoading] = useState(false);
    const [selectedManipulations, setSelectedManipulations] = useState<Record<string, boolean>>(
        Object.fromEntries(Object.keys(manipulationsColors).map((e) => [e, true]))
    );
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
            alert("Please provide a text for manipulation and emotion analysis.");
            return;
        }
        setLoading(true);
        try {
            const payload: SubmitRequest = { input_data };
            const response: DualAnalyze = await fetchAnalyzeManipulationsAndEmotions(payload);
            setAnalyzedData(response);
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
        a.download = "manipulation_and_emotion_analysis.json";
        a.click();
        URL.revokeObjectURL(url);
    };

    const renderText = () => {
        if (!analyzedData) return null;

        const selectedManipulationsTechniques = Object.keys(selectedManipulations).filter(
            (tech) => selectedManipulations[tech]
        );
        const selectedEmotionsTechniques = Object.keys(selectedEmotions).filter(
            (tech) => selectedEmotions[tech]
        );

        // Map paragraph index to array of HTML strings
        const paragraphs: Record<number, string[]> = {};

        // Process manipulations
        analyzedData.manipulations_analyzed.forEach((data) => {
            const { text, predictions, paragraphIndex } = data;
            const label = predictions?.[0]?.label || "none";

            const bgColor =
                selectedManipulationsTechniques.includes(label) && label !== "none"
                    ? manipulationsColors[label] || "#ccc"
                    : manipulationsColors["none"];

            // Build tooltip table
            let tooltipTable = "";
            if (predictions && predictions.length > 0 && label !== "none" && selectedManipulationsTechniques.includes(label)) {
                if (predictions.length === 1) {
                    tooltipTable = `<p>This is most likely a <b>${label}</b> manipulation, with probability: <b>${Math.round(predictions[0].score * 10000) / 100}%</b>.</p>`;
                } else {
                    tooltipTable = `<p><b>Most likely manipulations:</b></p><table>`;
                    predictions
                        .filter((p) => selectedManipulationsTechniques.includes(p.label))
                        .forEach((p) => {
                            tooltipTable += `<tr><td>${p.label}</td><td>${Math.round(p.score * 100)}%</td></tr>`;
                        });
                    tooltipTable += `</table>`;
                }
            }

            const showTooltip = tooltipTable.length > 0 && bgColor.toLowerCase() !== "#ffffff";

            const spanHtml = showTooltip
                ? `<span class="${styles.tooltip}" style="background-color: ${bgColor}; padding: 2px 4px; cursor: pointer;">
                ${text}
                <span class="${styles.tooltiptext}">${tooltipTable}</span>
               </span>`
                : `<span style="background-color: ${bgColor}; padding: 2px 4px;">
                ${text}
               </span>`;

            if (!paragraphs[paragraphIndex]) paragraphs[paragraphIndex] = [];
            paragraphs[paragraphIndex].push(spanHtml);
        });

        // Process emotions per paragraph
        Object.keys(paragraphs).forEach((pIndexStr) => {
            const pIndex = Number(pIndexStr);
            const emotionsForParagraph = analyzedData.emotions_analyzed.find(
                (e) => e.paragraphIndex === pIndex
            )?.predictions;

            if (emotionsForParagraph && emotionsForParagraph.length > 0) {
                const filtered = emotionsForParagraph.filter((e) => selectedEmotionsTechniques.includes(e.label));

                if (filtered.length > 0 && filtered[0].label != "neutral") {
                    let paragraphTooltip = "";
                    if (filtered.length === 1) {
                        paragraphTooltip = `<p>Most likely paragraph's emotion - <b>${filtered[0].label}</b>, probability: <b>${Math.round(filtered[0].score * 10000) / 100}%</b>.</p>`;
                    } else {
                        paragraphTooltip = `<p><b>Most likely paragraph's emotions:</b></p><table>`;
                        filtered.forEach((e) => {
                            paragraphTooltip += `<tr><td>${e.label}</td><td>${Math.round(e.score * 100)}%</td></tr>`;
                        });
                        paragraphTooltip += `</table>`;
                    }

                    // Wrap the paragraph content with tooltip span
                    paragraphs[pIndex] = [
                        `<span class="${styles.paragraphTooltip}">
      ${paragraphs[pIndex].join(" ")}
      <span class="${styles.paragraphTooltiptext}">${paragraphTooltip}</span>
  </span>`
                    ];
                }
            }
        });

        // Join and return as array of React fragments (each paragraph)
        return Object.keys(paragraphs)
            .sort((a, b) => Number(a) - Number(b))
            .map((pIndex) => (
                <React.Fragment key={`para-${pIndex}`}>
                    <div className={styles.paragraph} dangerouslySetInnerHTML={{ __html: paragraphs[Number(pIndex)].join(" ") }} />
                </React.Fragment>
            ));
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
                    Provide a text for <b>Manipulation and Emotion Analysis</b>:
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

                        <div className={`${styles.dropdownMenu} dropdown-menu p-3`} style={{ minWidth: "500px" }}>
                            <div className={`${styles.subDropdownDiv} d-flex justify-content-between`}>
                                {/* Manipulations column */}
                                <div className={`${styles.dropdownSubMenu} me-3`} style={{ flex: 1 }}>
                                    <p style={{textAlign: "center", marginTop: "16px"}}><b>Show manipulation techniques:</b></p>
                                    <hr />
                                    {Object.keys(selectedManipulations)
                                        .filter((e) => e !== "none")
                                        .map((manipulation) => (
                                            <li key={manipulation} className="dropdown-item">
                                                <label className={styles.checkboxLabel}>
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedManipulations[manipulation]}
                                                        onChange={() => toggleManipulation(manipulation)}
                                                        className={ `${ styles.formCheckInput } form-check-input me-2` }
                                                    />
                                                    {manipulation}
                                                </label>
                                            </li>
                                        ))}
                                </div>

                                {/* Emotions column */}
                                <div className={`${styles.dropdownSubMenu} me-3`} style={{ flex: 1 }}>
                                    <p style={{textAlign: "center", marginTop: "16px"}}><b>Show emotions expressed:</b></p>
                                    <hr />
                                    {Object.keys(selectedEmotions)
                                        .filter((e) => e !== "none")
                                        .map((emotion) => (
                                            <li key={emotion} className="dropdown-item">
                                                <label className={styles.checkboxLabel}>
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedEmotions[emotion]}
                                                        onChange={() => toggleEmotion(emotion)}
                                                        className={ `${ styles.formCheckInput } form-check-input me-2` }
                                                    />
                                                    {emotion}
                                                </label>
                                            </li>
                                        ))}
                                </div>
                            </div>
                        </div>
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
