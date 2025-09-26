import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Index from "./pages/index";

function App() {
    return (
        <BrowserRouter>
            <nav>
                <Link to="/">index</Link>
            </nav>
            <Routes>
                <Route path="/" element={<Index />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App;