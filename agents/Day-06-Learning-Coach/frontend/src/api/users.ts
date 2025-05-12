import api from './api';

interface User {
  id: number;
  username: string;
  email: string;
  preferences?: Record<string, any>;
  learning_styles?: string[];
  interests?: string[];
}

interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
}

interface UpdateUserRequest {
  username?: string;
  email?: string;
  password?: string;
  preferences?: Record<string, any>;
  learning_styles?: string[];
  interests?: string[];
}

export const getUsers = async (): Promise<User[]> => {
  const response = await api.get<User[]>('/users');
  return response.data;
};

export const getUser = async (id: number): Promise<User> => {
  const response = await api.get<User>(`/users/${id}`);
  return response.data;
};

export const createUser = async (user: CreateUserRequest): Promise<User> => {
  const response = await api.post<User>('/users', user);
  return response.data;
};

export const updateUser = async (id: number, user: UpdateUserRequest): Promise<User> => {
  const response = await api.put<User>(`/users/${id}`, user);
  return response.data;
};

export const deleteUser = async (id: number): Promise<void> => {
  await api.delete(`/users/${id}`);
};
