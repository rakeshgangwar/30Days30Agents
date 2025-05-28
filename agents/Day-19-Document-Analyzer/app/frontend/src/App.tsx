import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Header from './components/Header'
import './App.css'

function App() {
  return (
    
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <div className="max-w-7xl mx-auto px-4">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/chat/:documentId" element={<Chat />} />
            </Routes>
          </div>
          
        </div>
      </Router>
    
  )
}

export default App
