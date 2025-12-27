import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
});

export interface Category {
  id: string;
  name: string;
  slug: string;
  sheet_id?: string;
  sheet_url?: string;
  sheets_synced_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Article {
  id: string;
  category_id: string;
  keyword: string;
  title?: string;
  content?: string;
  status: 'pending' | 'generating' | 'failed' | 'review_pending' | 'reviewed' | 'published';
  wp_post_id?: number;
  wp_url?: string;
  wp_published_at?: string;
  metadata_?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ArticleListResponse {
  items: Article[];
  total: number;
  page: number;
  per_page: number;
}

export const categoriesApi = {
  list: () => api.get<Category[]>('/categories'),
  create: (data: { name: string; slug: string }) => api.post<Category>('/categories', data),
  get: (id: string) => api.get<Category>(`/categories/${id}`),
  update: (id: string, data: { name?: string; slug?: string }) =>
    api.patch<Category>(`/categories/${id}`, data),
  delete: (id: string) => api.delete(`/categories/${id}`),
};

export const articlesApi = {
  list: (params?: { category_id?: string; status?: string; page?: number; per_page?: number }) =>
    api.get<ArticleListResponse>('/articles', { params }),
  create: (data: { category_id: string; keyword: string; prompt_template_id?: string }) =>
    api.post<Article>('/articles', data),
  get: (id: string) => api.get<Article>(`/articles/${id}`),
  update: (id: string, data: { keyword?: string; title?: string; content?: string; status?: string }) =>
    api.patch<Article>(`/articles/${id}`, data),
  delete: (id: string) => api.delete(`/articles/${id}`),
  generate: (id: string, options?: Record<string, any>) =>
    api.post(`/generate`, { article_id: id, options }),
  regenerate: (id: string, options?: Record<string, any>) =>
    api.post(`/generate/regenerate/${id}`, options),
  batchGenerate: (ids: string[], options?: Record<string, any>) =>
    api.post('/batch/generate', { article_ids: ids, options }),
};

export const sheetsApi = {
  create: (categoryId: string) => api.post('/sheets/create', { category_id: categoryId }),
  link: (categoryId: string, sheetId: string, sheetUrl: string) =>
    api.post('/sheets/link', { category_id: categoryId, sheet_id: sheetId, sheet_url: sheetUrl }),
};

export const wordpressApi = {
  draft: (articleId: string) => api.post('/wordpress/draft', { article_id: articleId }),
  publish: (articleId: string) => api.post('/wordpress/publish', { article_id: articleId }),
};

export const batchApi = {
  generate: (articleIds: string[], options?: Record<string, any>) =>
    api.post('/batch/generate', { article_ids: articleIds, options }),
  status: (jobId: string) => api.get(`/batch/status/${jobId}`),
  generateSingle: (articleId: string) =>
    api.post(`/batch/generate/single/${articleId}`),
};

export default api;
