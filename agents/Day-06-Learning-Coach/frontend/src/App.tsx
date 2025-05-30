import { Routes, Route } from 'react-router-dom';
import { Box } from '@chakra-ui/react';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import LearningPathsPage from './pages/LearningPathsPage';
import LearningPathViewPage from './pages/LearningPathViewPage';
import ResourcesPage from './pages/ResourcesPage';
import QuizzesPage from './pages/QuizzesPage';
import QuizAttemptPage from './pages/QuizAttemptPage';
import NotFoundPage from './pages/NotFoundPage';
import Layout from './components/Layout';

function App() {
  return (
    <Box>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="learning-paths" element={<LearningPathsPage />} />
          <Route path="learning-paths/:id" element={<LearningPathViewPage />} />
          <Route path="resources" element={<ResourcesPage />} />
          <Route path="quizzes" element={<QuizzesPage />} />
          <Route path="quizzes/:id" element={<QuizAttemptPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Box>
  );
}

export default App;
