import api from './api';

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  question_type: string;
}

export interface Quiz {
  id: string;
  title: string;
  description: string;
  topic: string;
  difficulty: string;
  questions: QuizQuestion[];
  estimated_time_minutes: number;
  created_at: string;
  learning_objectives?: string[];
  tags?: string[];
  user_id?: number;
}

export interface QuizAttempt {
  id: string;
  quiz_id: string;
  user_id?: number;
  answers: number[];
  score: number;
  correct_answers: number;
  total_questions: number;
  feedback?: any;
  completed_at: string;
}

export interface GenerateQuizRequest {
  topic: string;
  difficulty?: string;
  num_questions?: number;
  question_types?: string[];
  learning_objectives?: string[];
  user_id?: number;
}

export const getQuizzes = async (
  topic?: string,
  difficulty?: string,
  user_id?: number
): Promise<Quiz[]> => {
  let url = '/quizzes';
  const params = new URLSearchParams();
  
  if (topic) params.append('topic', topic);
  if (difficulty) params.append('difficulty', difficulty);
  if (user_id) params.append('user_id', user_id.toString());
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await api.get<Quiz[]>(url);
  return response.data;
};

export const getQuiz = async (id: string): Promise<Quiz> => {
  const response = await api.get<Quiz>(`/quizzes/${id}`);
  return response.data;
};

export const generateQuiz = async (request: GenerateQuizRequest): Promise<Quiz> => {
  const response = await api.post<Quiz>('/quizzes/generate', request);
  return response.data;
};

export const submitQuizAttempt = async (
  quiz_id: string,
  answers: number[],
  user_id?: number
): Promise<QuizAttempt> => {
  const response = await api.post<QuizAttempt>(`/quizzes/${quiz_id}/submit`, {
    answers,
    user_id: user_id?.toString()
  });
  return response.data;
};

// Function to save a quiz from the chat interface
export const saveQuizFromChat = async (quiz: any): Promise<Quiz> => {
  // The quiz from chat should already be in the correct format
  // We just need to make sure it has the required fields
  const generateRequest: GenerateQuizRequest = {
    topic: quiz.topic,
    difficulty: quiz.difficulty,
    num_questions: quiz.questions.length,
    question_types: ['multiple_choice'],
    learning_objectives: quiz.learning_objectives || []
  };
  
  // We're not actually generating a new quiz, but using the API endpoint
  // to save the existing quiz to the database
  const response = await api.post<Quiz>('/quizzes/generate', {
    ...generateRequest,
    // Include the existing quiz data
    existing_quiz: quiz
  });
  
  return response.data;
};
