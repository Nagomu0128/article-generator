# タスク09: フロントエンド実装

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 3時間 |
| 前提条件 | タスク08完了 |
| 成果物 | Next.js 全画面 |

---

## 📁 ディレクトリ構造

```
frontend/src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                 # ダッシュボード
│   ├── categories/
│   │   ├── page.tsx             # カテゴリ一覧
│   │   └── [id]/page.tsx        # カテゴリ詳細
│   └── articles/
│       ├── page.tsx             # 記事一覧
│       └── [id]/page.tsx        # 記事詳細
├── components/
│   ├── layout/
│   │   ├── header.tsx
│   │   └── sidebar.tsx
│   ├── articles/
│   │   ├── article-list.tsx
│   │   └── article-card.tsx
│   └── categories/
│       └── category-card.tsx
├── lib/
│   ├── api.ts
│   └── utils.ts
├── hooks/
│   └── use-api.ts
└── types/
    └── index.ts
```

---

## 📝 実装ファイル

### frontend/src/lib/api.ts

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
});

export interface Category {
  id: string;
  name: string;
  slug: string;
  sheet_url?: string;
  created_at: string;
}

export interface Article {
  id: string;
  category_id: string;
  keyword: string;
  title?: string;
  content?: string;
  status: 'pending' | 'generating' | 'failed' | 'review_pending' | 'reviewed' | 'published';
  wp_url?: string;
  created_at: string;
}

export const categoriesApi = {
  list: () => api.get<Category[]>('/categories'),
  create: (data: { name: string; slug: string }) => api.post<Category>('/categories', data),
  get: (id: string) => api.get<Category>(`/categories/${id}`),
  delete: (id: string) => api.delete(`/categories/${id}`),
};

export const articlesApi = {
  list: (params?: { category_id?: string; status?: string; page?: number }) =>
    api.get<{ items: Article[]; total: number }>('/articles', { params }),
  create: (data: { category_id: string; keyword: string }) => api.post<Article>('/articles', data),
  get: (id: string) => api.get<Article>(`/articles/${id}`),
  generate: (id: string, options?: object) => api.post(`/generate`, { article_id: id, options }),
  batchGenerate: (ids: string[]) => api.post('/batch/generate', { article_ids: ids }),
};

export const wordpressApi = {
  draft: (articleId: string) => api.post('/wordpress/draft', { article_id: articleId }),
  publish: (articleId: string) => api.post('/wordpress/publish', { article_id: articleId }),
};

export default api;
```

### frontend/src/types/index.ts

```typescript
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
```

### frontend/src/app/layout.tsx

```typescript
import './globals.css';
import { Inter } from 'next/font/google';
import { Toaster } from '@/components/ui/toaster';
import { QueryProvider } from '@/components/providers/query-provider';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <QueryProvider>
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col">
              <Header />
              <main className="flex-1 overflow-auto p-6 bg-gray-50">
                {children}
              </main>
            </div>
          </div>
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}
```

### frontend/src/components/layout/sidebar.tsx

```typescript
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, FolderOpen, FileText, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'ダッシュボード', href: '/', icon: Home },
  { name: 'カテゴリ', href: '/categories', icon: FolderOpen },
  { name: '記事', href: '/articles', icon: FileText },
  { name: '設定', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-white border-r">
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold">記事生成システム</h1>
      </div>
      <nav className="p-4 space-y-1">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-md text-sm',
              pathname === item.href
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            <item.icon className="w-5 h-5" />
            {item.name}
          </Link>
        ))}
      </nav>
    </div>
  );
}
```

### frontend/src/app/page.tsx（ダッシュボード）

```typescript
'use client';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { articlesApi, categoriesApi } from '@/lib/api';
import { STATUS_LABELS } from '@/types';

export default function DashboardPage() {
  const { data: articles } = useQuery({
    queryKey: ['articles'],
    queryFn: () => articlesApi.list({ page: 1 }),
  });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesApi.list(),
  });

  const stats = articles?.data.items.reduce((acc, a) => {
    acc[a.status] = (acc[a.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">ダッシュボード</h1>

      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">総記事数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{articles?.data.total || 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">レビュー待ち</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-yellow-600">{stats.review_pending || 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">公開済み</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{stats.published || 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">カテゴリ数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{categories?.data.length || 0}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### frontend/src/app/articles/page.tsx（記事一覧）

```typescript
'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { articlesApi } from '@/lib/api';
import { STATUS_LABELS, STATUS_COLORS, ArticleStatus } from '@/types';
import { useToast } from '@/components/ui/use-toast';
import Link from 'next/link';

export default function ArticlesPage() {
  const [selected, setSelected] = useState<string[]>([]);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles'],
    queryFn: () => articlesApi.list(),
  });

  const generateMutation = useMutation({
    mutationFn: (id: string) => articlesApi.generate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      toast({ title: '生成を開始しました' });
    },
  });

  const batchMutation = useMutation({
    mutationFn: (ids: string[]) => articlesApi.batchGenerate(ids),
    onSuccess: () => {
      setSelected([]);
      toast({ title: 'バッチ生成を開始しました' });
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">記事一覧</h1>
        <div className="space-x-2">
          {selected.length > 0 && (
            <Button onClick={() => batchMutation.mutate(selected)}>
              選択した{selected.length}件を生成
            </Button>
          )}
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">
              <input
                type="checkbox"
                onChange={(e) => setSelected(e.target.checked ? articles?.data.items.map(a => a.id) || [] : [])}
              />
            </TableHead>
            <TableHead>キーワード</TableHead>
            <TableHead>タイトル</TableHead>
            <TableHead>ステータス</TableHead>
            <TableHead>操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {articles?.data.items.map((article) => (
            <TableRow key={article.id}>
              <TableCell>
                <input
                  type="checkbox"
                  checked={selected.includes(article.id)}
                  onChange={(e) => setSelected(
                    e.target.checked
                      ? [...selected, article.id]
                      : selected.filter(id => id !== article.id)
                  )}
                />
              </TableCell>
              <TableCell>{article.keyword}</TableCell>
              <TableCell>{article.title || '-'}</TableCell>
              <TableCell>
                <Badge className={STATUS_COLORS[article.status as ArticleStatus]}>
                  {STATUS_LABELS[article.status as ArticleStatus]}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="space-x-2">
                  <Link href={`/articles/${article.id}`}>
                    <Button variant="outline" size="sm">詳細</Button>
                  </Link>
                  {article.status === 'pending' && (
                    <Button size="sm" onClick={() => generateMutation.mutate(article.id)}>
                      生成
                    </Button>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

### frontend/src/components/providers/query-provider.tsx

```typescript
'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: { staleTime: 60 * 1000 },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

---

## ✅ 完了条件

```bash
# フロントエンドが起動する
cd frontend && npm run dev
# http://localhost:3000 → ダッシュボードが表示される

# 以下の画面が動作する
# - ダッシュボード（統計表示）
# - カテゴリ一覧
# - 記事一覧（チェックボックス、バッチ生成）
# - 記事詳細
```

---

## 📌 次のタスク

タスク09完了後、**タスク10: 結合テスト・デプロイ** に進んでください。
