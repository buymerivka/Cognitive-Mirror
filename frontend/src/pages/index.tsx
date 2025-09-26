import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
// Bootstrap CSS
import "bootstrap/dist/css/bootstrap.min.css";
// Bootstrap JS (опційно, якщо потрібні JS-компоненти)
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import '../index.css'
import styles from "./Index.module.css";

interface Endpoint {
    title: string;
    description: string;
    link: string;
}

const endpoints: Endpoint[] = [
    {
        title: "Full Analysis",
        description:
            "Runs the full pipeline: identifies sentences with Russian propaganda (Russo-Ukrainian war context) and, within those sentences, detects expressed emotions and logical fallacies.",
        link: "/analyze",
    },
    {
        title: "Manipulation & Emotion Analysis",
        description:
            "Checks for manipulative techniques at the sentence level and analyzes emotions at the paragraph level for broader context.",
        link: "/analyze_manipulations_and_emotions",
    },
    {
        title: "Propaganda Analysis",
        description:
            "Highlights sentences containing Russian propaganda (Russo-Ukrainian war context) and distinguishes them from neutral ones.",
        link: "/analyze_propaganda",
    },
    {
        title: "Manipulation Analysis",
        description:
            "Detects specific manipulation techniques in each sentence, including false dilemmas, slippery slopes, appeals to authority, majority, tradition, and more.",
        link: "/analyze_manipulations",
    },
    {
        title: "Emotion Analysis",
        description:
            "Analyzes each sentence for emotions such as anger, joy, fear, sadness, love, surprise, admiration, and others.",
        link: "/analyze_emotions",
    },
];

const Index: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div id="root">
            <Header />
            <div className={styles.container}>
                <main className={styles.main}>
                    <h2 className={styles.title}>Please check out our tools:</h2>

                    <div className={styles.cardList}>
                        {endpoints.map((ep) => (
                            <div
                                key={ep.link}
                                className={`${styles.card} ${
                                    ep.title === "Analyze Propaganda" ? styles.lastCard : ""
                                }`}
                                onClick={() => navigate(ep.link)}
                            >
                                <h3 className={styles.cardTitle}>{ep.title}</h3>
                                <p className={styles.cardDescription}>{ep.description}</p>
                            </div>
                        ))}
                    </div>
                </main>
            </div>
            <Footer />
        </div>

    );
};

export default Index;
