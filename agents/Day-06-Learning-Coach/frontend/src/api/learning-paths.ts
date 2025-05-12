import api from './api';

export interface LearningPathTopic {
  name: string;
  order: number;
}

export interface LearningPathResource {
  name?: string;
  title?: string;
  url: string;
  type: string;
  description: string;
  topic_order?: number;
  topic_id?: number | string;
  topic_name?: string;
  topics?: Array<string | { name: string; order?: number }>;
  topic?: {
    order: number;
    name?: string;
  };
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  topics: LearningPathTopic[];
  resources: LearningPathResource[];
  user_id?: number;
  created_at: string;
  updated_at: string;
  progress: {
    completed_topics: number;
    total_topics: number;
    completed_topic_ids?: number[] | string[];
  };
}

export interface CreateLearningPathRequest {
  title: string;
  description: string;
  topics: LearningPathTopic[];
  resources: LearningPathResource[];
  user_id?: number;
  progress?: {
    completed_topics: number;
    total_topics: number;
    completed_topic_ids?: number[];
  };
}

export const getLearningPaths = async (): Promise<LearningPath[]> => {
  const response = await api.get<LearningPath[]>('/paths');
  return response.data;
};

export const getLearningPath = async (id: number): Promise<LearningPath> => {
  const response = await api.get<LearningPath>(`/paths/${id}`);
  return response.data;
};

export const createLearningPath = async (learningPath: CreateLearningPathRequest): Promise<LearningPath> => {
  const response = await api.post<LearningPath>('/paths', learningPath);
  return response.data;
};

export const updateLearningPath = async (id: number, learningPath: Partial<CreateLearningPathRequest>): Promise<LearningPath> => {
  const response = await api.put<LearningPath>(`/paths/${id}`, learningPath);
  return response.data;
};

export const deleteLearningPath = async (id: number): Promise<void> => {
  await api.delete(`/paths/${id}`);
};

// Function to save a learning path from the chat interface
export const saveLearningPathFromChat = async (learningPath: any): Promise<LearningPath> => {
  // Transform the learning path from the chat format to the API format
  const createRequest: CreateLearningPathRequest = {
    title: learningPath.title,
    description: learningPath.description,
    topics: learningPath.topics.map((topic: any, index: number) => ({
      name: topic.title,
      order: index + 1
    })),
    resources: learningPath.topics.flatMap((topic: any, topicIndex: number) =>
      topic.resources.map((resource: any) => ({
        name: resource.title,
        url: resource.url,
        type: resource.type,
        description: resource.description || '',
        topic_order: topicIndex + 1,
        topic_id: topicIndex + 1,
        topic_name: topic.title,
        topics: [topic.title],
        topic: {
          order: topicIndex + 1,
          name: topic.title
        }
      }))
    )
  };

  return createLearningPath(createRequest);
};
