import { BrowserRouter, Routes, Route } from "react-router-dom";

const App = () => (
  <BrowserRouter basename="/">
    <Routes>
      <Route path="/" element={<div style={{ padding: "2rem", textAlign: "center" }}><h1>Finnish Learning App</h1><p>Skeleton - Ready for development</p></div>} />
      <Route path="*" element={<div style={{ padding: "2rem", textAlign: "center" }}><h1>404 - Not Found</h1></div>} />
    </Routes>
  </BrowserRouter>
);

export default App;
