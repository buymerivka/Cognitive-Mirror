import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Index from "./pages/index";
import AnalyzeEmotions from "./pages/analyze_emotions";

function App() {
    return (
        <BrowserRouter>
            <nav>
                <Link to="/">index</Link>
            </nav>
            <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/analyze_emotions" element={<AnalyzeEmotions />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App;