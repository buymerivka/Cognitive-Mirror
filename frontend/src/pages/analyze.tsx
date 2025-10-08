import React, { useState, useRef } from "react";
import { fetchAnalyze } from "../api/client.ts";
import type { SubmitRequest, FullAnalyze } from "../api/client.ts";
import Header from "../components/Header";
import Footer from "../components/Footer";
import styles from "./analyze.module.css";
import TextareaAutosize from 'react-textarea-autosize';

const MAX_CHAR = 2048;

const filterOptions: string[] = [
    'Show manipulation techniques',
    'Show emotions expressed',
];

const PropagandaColors: Record<string, string> = {
    'LABEL_0': '#ffffff',      // White
    'LABEL_1': '#cd5c5c',      // Indian red
};

const Analyze: React.FC = () => {
    const [input_data, setText] = useState("");
    const [analyzedData, setAnalyzedData] = useState<{
        propaganda_analyzed: FullAnalyze["propaganda_analyzed"];
        manipulations_analyzed: FullAnalyze["manipulations_analyzed"];
        emotions_analyzed: FullAnalyze["emotions_analyzed"];
    } | null>(null);
    const [loading, setLoading] = useState(false);
    const [selectedFilters, setSelectedFilters] = useState<Record<string, boolean>>(
        Object.fromEntries(filterOptions.map((filter) => [filter, true]))
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
            alert("Please provide a text for analysis.");
            return;
        }
        setLoading(true);
        try {
            const payload: SubmitRequest = { input_data };
            const response: FullAnalyze = await fetchAnalyze(payload);
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
        setSelectedFilters(
            Object.fromEntries(Object.keys(filterOptions).map((e) => [e, true]))
        );
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
        }
    };

    const toggleFilters = (filter: string) => {
        setSelectedFilters((prev) => ({ ...prev, [filter]: !prev[filter] }));
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

        const showManipulations = selectedFilters['Show manipulation techniques'];
        const showEmotions = selectedFilters['Show emotions expressed'];

        let isLastInParagraph = false;

        return analyzedData.propaganda_analyzed.map((data, idx) => {
            isLastInParagraph = false;
            if (
                idx < analyzedData.propaganda_analyzed.length - 1 &&
                analyzedData.propaganda_analyzed[idx + 1].paragraphIndex !== data.paragraphIndex
            ) {
                isLastInParagraph = true;
            }

            const pPredictions = data.predictions;
            const label = pPredictions?.[0]?.label || 'LABEL_0';
            const color = PropagandaColors[label] || '#ffffff';

            // Tooltip content array
            const tooltipContent: string[] = [];

            // Propaganda info
            if (label === 'LABEL_1') {
                tooltipContent.push(
                    `<p style="margin: 0">This is most likely a <b>propagandistic</b> sentence, probability: <b>${Math.round(
                        pPredictions[0].score * 10000
                    ) / 100}%</b>.</p>`
                );
            }

            // Find corresponding manipulation by matching text
            if (showManipulations) {
                const mData = analyzedData.manipulations_analyzed.find((m) => m.text === data.text);
                if (mData && mData.predictions.length > 0) {
                    const mPred = mData.predictions[0];
                    tooltipContent.push(
                        `<p style="margin: 0">Most likely manipulation technique - <b>${mPred.label}</b>, probability: <b>${Math.round(
                            mPred.score * 10000
                        ) / 100}%</b>.</p>`
                    );
                }
            }

            // Find corresponding emotion by matching text
            if (showEmotions) {
                const eData = analyzedData.emotions_analyzed.find((e) => e.text === data.text);
                if (eData && eData.predictions.length > 0) {
                    const ePred = eData.predictions[0];
                    tooltipContent.push(
                        `<p style="margin: 0">Most likely emotion expressed - <b>${ePred.label}</b>, probability: <b>${Math.round(
                            ePred.score * 10000
                        ) / 100}%</b>.</p>`
                    );
                }
            }

            // Show tooltip only if content exists
            const showTooltip = tooltipContent.length > 0;

            return (
                <React.Fragment key={idx}>
                    {showTooltip ? (
                        <span className={styles.tooltip} style={{ backgroundColor: color }}>
                        {data.text}
                            <div
                                className={styles.tooltiptext}
                                dangerouslySetInnerHTML={{ __html: tooltipContent.join('') }}
                            />
                            {isLastInParagraph && <br />}
                    </span>
                    ) : (
                        <span>
                        {data.text}
                            {isLastInParagraph && <br />}
                    </span>
                    )}
                </React.Fragment>
            );
        });
    };



    // const renderText = () => {
    //     if (!analyzedData) return null;
    //
    //     const showManipulations = selectedFilters['Show manipulation techniques'];
    //     const showEmotions = selectedFilters['Show emotions expressed'];
    //
    //     const parts: string[] = [];
    //     let lastParagraphId = -1;
    //
    //     analyzedData.propaganda_analyzed.forEach((data, idx) => {
    //         const { text, predictions, paragraphIndex } = data;
    //
    //         // Propaganda color
    //         const bgColor = PropagandaColors[predictions[0].label];
    //
    //         let tooltipHtml = '';
    //
    //         // Propaganda info
    //         if (predictions && predictions[0].label !== 'LABEL_0') {
    //             const pPred = predictions[0];
    //             tooltipHtml += `<p>This is most likely a <b>propagandistic</b> sentence, probability: <b>${Math.round(pPred.score * 10000) / 100}%</b>.</p>`;
    //         }
    //
    //         // Manipulation info
    //         if (showManipulations && idx < analyzedData.manipulations_analyzed.length) {
    //             const mData = analyzedData.manipulations_analyzed[idx];
    //             if (mData.text === text && mData.predictions.length > 0) {
    //                 const mPred = mData.predictions[0];
    //                 tooltipHtml += `<p>Most likely manipulation technique - <b>${mPred.label}</b>, probability: <b>${Math.round(mPred.score * 10000) / 100}%</b>.</p>`;
    //             }
    //         }
    //
    //         // Emotion info
    //         if (showEmotions && idx < analyzedData.emotions_analyzed.length) {
    //             const eData = analyzedData.emotions_analyzed[idx];
    //             if (eData.text === text && eData.predictions.length > 0) {
    //                 const ePred = eData.predictions[0];
    //                 tooltipHtml += `<p>Most likely emotion expressed - <b>${ePred.label}</b>, probability: <b>${Math.round(ePred.score * 10000) / 100}%</b>.</p>`;
    //             }
    //         }
    //
    //         // Show tooltip only if we have content
    //         const showTooltip = tooltipHtml.length > 0;
    //
    //         let spanHtml = showTooltip
    //             ? `<span class="tooltip" style="background-color: ${bgColor}; padding: 2px 4px;">
    //                 ${text}
    //                 <span class="tooltiptext">${tooltipHtml}</span>
    //            </span>`
    //             : `<span style="background-color: ${bgColor}; padding: 2px 4px;">${text}</span>`;
    //
    //         if (lastParagraphId !== paragraphIndex) {
    //             spanHtml = '<br>' + spanHtml;
    //             lastParagraphId = paragraphIndex;
    //         }
    //
    //         parts.push(spanHtml);
    //     });
    //
    //     return (
    //         <div
    //             style={{ fontSize: '18px', lineHeight: 1.6, textAlign: 'justify' }}
    //             dangerouslySetInnerHTML={{ __html: parts.join(' ') }}
    //         />
    //     );
    // };



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
                    Provide a text for <b>Full Analysis</b>:
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
                            {Object.keys(selectedFilters)
                                .filter((e) => e !== "neutral")
                                .map((emotion) => (
                                    <li key={emotion} className="dropdown-item" style={{paddingLeft: "0"}}>
                                        <label className={styles.checkboxLabel}>
                                            <input
                                                type="checkbox"
                                                checked={selectedFilters[emotion]}
                                                onChange={() => toggleFilters(emotion)}
                                                className={ `${ styles.formCheckInput } form-check-input me-2` }
                                            />
                                            {emotion}
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

export default Analyze;
