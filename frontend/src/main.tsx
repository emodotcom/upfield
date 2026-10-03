import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { ThemeProvider } from "./components/theme-provider";
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="upfield-theme">
      <BrowserRouter>
        <div className="min-h-screen bg-background font-sans antialiased text-foreground">
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
)
