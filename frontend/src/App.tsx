import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Index from "./pages/index";
import AnalyzeEmotions from "./pages/analyze_emotions";
import AnalyzeManipulations from "./pages/analyze_manipulations";
import AnalyzePropaganda from "./pages/analyze_propaganda";
import AnalyzeManipulationsAndEmotions from "./pages/analyze_manipulation_and_emotions";
import Analyze from "./pages/analyze";

function App() {
    return (
        <BrowserRouter>
            <nav>
                <Link to="/">index</Link>
            </nav>
            <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/analyze_emotions" element={<AnalyzeEmotions />} />
                <Route path="/analyze_manipulations" element={<AnalyzeManipulations />} />
                <Route path="/analyze_propaganda" element={<AnalyzePropaganda />} />
                <Route path="/analyze_manipulations_and_emotions" element={<AnalyzeManipulationsAndEmotions />} />
                <Route path="/analyze" element={<Analyze />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App;