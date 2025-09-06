import React from 'react'
import { Routes, Route } from 'react-router-dom'
import HomePage from './components/HomePage'
import UnsubscribePage from './components/UnsubscribePage'
import NewsletterPreviewPage from './components/NewsletterPreviewPage'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/unsubscribe/:token" element={<UnsubscribePage />} />
        <Route path="/newsletter/:id" element={<NewsletterPreviewPage />} />
      </Routes>
    </div>
  )
}

export default App