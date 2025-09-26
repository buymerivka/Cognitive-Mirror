import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Header.module.css";
import logo from "../assets/logo.png";

const Header: React.FC = () => {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);

    const endpoints = [
        { title: "Full Analysis", link: "/analyze" },
        { title: "Manipulation & Emotion Analysis", link: "/analyze_manipulations_and_emotions" },
        { title: "Propaganda Analysis", link: "/analyze_propaganda" },
        { title: "Manipulation Analysis", link: "/analyze_manipulations" },
        { title: "Emotion Analysis", link: "/analyze_emotions" },
    ];

    const toggleMenu = () => setOpen(!open);

    return (
        <header className={styles.header}>
            {/* Лівий блок: Назва */}
            <div className={styles.headerColumn}>
                <a className={styles.title} onClick={() => navigate("/")}>
                    <img src={logo} alt="Logo" className={styles.logo}/>Cognitive Mirror
                </a>
            </div>

            <div className={styles.burgerWrapper}>
                <button className={`${styles.burgerButton} ${open ? styles.burgerOpen : ""}`} onClick={toggleMenu}>
                    {open ? "Available tools" : "☰"}
                </button>

                {open && (
                    <div className={styles.dropdownMenu}>
                        {endpoints.map((ep, index) => (
                            <React.Fragment key={ep.link}>
                                <div
                                    className={styles.menuItem}
                                    onClick={() => {
                                        navigate(ep.link);
                                        setOpen(false);
                                    }}
                                >
                                    {ep.title}
                                </div>
                                {index < endpoints.length - 1 && <hr className={styles.separator} />}
                            </React.Fragment>
                        ))}
                    </div>
                )}
            </div>
        </header>
    );
};

export default Header;
