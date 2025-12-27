export type ArticleStatus = 'pending' | 'generating' | 'failed' | 'review_pending' | 'reviewed' | 'published';

export const STATUS_LABELS: Record<ArticleStatus, string> = {
  pending: '未生成',
  generating: '生成中',
  failed: '生成失敗',
  review_pending: 'レビュー待ち',
  reviewed: 'レビュー済み',
  published: '公開済み',
};

export const STATUS_COLORS: Record<ArticleStatus, string> = {
  pending: 'bg-gray-100 text-gray-800',
  generating: 'bg-blue-100 text-blue-800',
  failed: 'bg-red-100 text-red-800',
  review_pending: 'bg-yellow-100 text-yellow-800',
  reviewed: 'bg-green-100 text-green-800',
  published: 'bg-purple-100 text-purple-800',
};
