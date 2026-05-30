import React from "react";
import styles from "./Footer.module.css";

const Footer: React.FC = () => {
    const copyEmail = () => {
        navigator.clipboard.writeText("buymerivka@gmail.com");
        alert("Email copied to clipboard!");
    };

    return (
        <footer className={styles.footer}>
            <div className={styles.footerLeft}>
                <h1>Cognitive Mirror</h1>
                <p>AI tool for analyzing text propaganda, manipulations and emotions</p>
                <p>Feel free to contact us:</p>
                <p className={styles.email} onClick={copyEmail}>
                    buymerivka@gmail.com
                </p>
            </div>

            <div className={styles.footerColumns}>
                {/* Column 1 */}
                <div className={styles.column}>
                    <span className={styles.title}>Arsenii Galaida</span>
                    <div className={styles.links}>
            <span
                className={styles.link}
                onClick={() =>
                    window.open("https://github.com/ArseniiGalaida", "_blank")
                }
            >
              GitHub
            </span>
                        <span
                            className={styles.link}
                            onClick={() =>
                                window.open("https://www.linkedin.com/in/arsenii-galaida", "_blank")
                            }
                        >
              LinkedIn
            </span>
                    </div>
                </div>

                {/* Column 2 */}
                <div className={styles.column}>
                    <span className={styles.title}>Yehor Kuzmych</span>
                    <div className={styles.links}>
            <span
                className={styles.link}
                onClick={() => window.open("https://github.com/yehor-kuzmych", "_blank")}
            >
              GitHub
            </span>
                        <span
                            className={styles.link}
                            onClick={() =>
                                window.open(
                                    "https://www.linkedin.com/in/yehor-kuzmych-b78453353",
                                    "_blank"
                                )
                            }
                        >
              LinkedIn
            </span>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
