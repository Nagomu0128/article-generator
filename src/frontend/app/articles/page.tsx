'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { articlesApi } from '@/lib/api';
import { STATUS_LABELS, STATUS_COLORS, ArticleStatus } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { Eye, Play } from 'lucide-react';
import { CreateArticleDialog } from '@/components/create-article-dialog';

export default function ArticlesPage() {
  const [selected, setSelected] = useState<string[]>([]);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: articlesData, isLoading } = useQuery({
    queryKey: ['articles'],
    queryFn: async () => {
      const response = await articlesApi.list({ page: 1, per_page: 100 });
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 記事は2分間キャッシュ
  });

  const generateMutation = useMutation({
    mutationFn: (id: string) => articlesApi.generate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      toast({ title: '生成を開始しました' });
    },
    onError: () => {
      toast({ title: '生成に失敗しました', variant: 'destructive' });
    },
  });

  const batchMutation = useMutation({
    mutationFn: (ids: string[]) => articlesApi.batchGenerate(ids),
    onSuccess: () => {
      setSelected([]);
      toast({ title: `バッチ生成を開始しました (${selected.length}件)` });
    },
    onError: () => {
      toast({ title: 'バッチ生成に失敗しました', variant: 'destructive' });
    },
  });

  const articles = articlesData?.items || [];
  const allSelected = articles.length > 0 && selected.length === articles.length;

  const toggleAll = () => {
    if (allSelected) {
      setSelected([]);
    } else {
      setSelected(articles.map((a) => a.id));
    }
  };

  const toggleItem = (id: string) => {
    if (selected.includes(id)) {
      setSelected(selected.filter((sid) => sid !== id));
    } else {
      setSelected([...selected, id]);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">記事一覧</h1>
          <p className="text-gray-500 mt-1">
            全{articlesData?.total || 0}件の記事
          </p>
        </div>
        <div className="space-x-2">
          {selected.length > 0 && (
            <Button
              onClick={() => batchMutation.mutate(selected)}
              disabled={batchMutation.isPending}
            >
              <Play className="w-4 h-4 mr-2" />
              選択した{selected.length}件を生成
            </Button>
          )}
          <CreateArticleDialog />
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">読み込み中...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border">
          <p className="text-gray-500">記事がありません</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={toggleAll}
                    className="rounded border-gray-300"
                  />
                </TableHead>
                <TableHead>キーワード</TableHead>
                <TableHead>タイトル</TableHead>
                <TableHead>ステータス</TableHead>
                <TableHead>作成日時</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {articles.map((article) => (
                <TableRow key={article.id}>
                  <TableCell>
                    <input
                      type="checkbox"
                      checked={selected.includes(article.id)}
                      onChange={() => toggleItem(article.id)}
                      className="rounded border-gray-300"
                    />
                  </TableCell>
                  <TableCell className="font-medium">{article.keyword}</TableCell>
                  <TableCell className="text-gray-600">
                    {article.title || '-'}
                  </TableCell>
                  <TableCell>
                    <Badge className={STATUS_COLORS[article.status as ArticleStatus]}>
                      {STATUS_LABELS[article.status as ArticleStatus]}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-gray-500">
                    {new Date(article.created_at).toLocaleDateString('ja-JP')}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link href={`/articles/${article.id}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-1" />
                          詳細
                        </Button>
                      </Link>
                      {article.status === 'pending' && (
                        <Button
                          size="sm"
                          onClick={() => generateMutation.mutate(article.id)}
                          disabled={generateMutation.isPending}
                        >
                          <Play className="w-4 h-4 mr-1" />
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
      )}
    </div>
  );
}
