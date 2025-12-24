'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { articlesApi, categoriesApi } from '@/lib/api';
import { STATUS_LABELS, ArticleStatus } from '@/types';
import { FileText, FolderOpen, CheckCircle, Clock } from 'lucide-react';

export default function DashboardPage() {
  const { data: articlesData } = useQuery({
    queryKey: ['articles'],
    queryFn: async () => {
      const response = await articlesApi.list({ page: 1, per_page: 1000 });
      return response.data;
    },
  });

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await categoriesApi.list();
      return response.data;
    },
  });

  const stats = (articlesData?.items || []).reduce((acc, article) => {
    acc[article.status] = (acc[article.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const cards = [
    {
      title: '総記事数',
      value: articlesData?.total || 0,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'レビュー待ち',
      value: stats.review_pending || 0,
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: '公開済み',
      value: stats.published || 0,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'カテゴリ数',
      value: categoriesData?.length || 0,
      icon: FolderOpen,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">ダッシュボード</h1>
        <p className="text-gray-500 mt-1">記事生成システムの概要</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.title}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-gray-500">
                    {card.title}
                  </CardTitle>
                  <div className={`p-2 rounded-lg ${card.bgColor}`}>
                    <Icon className={`w-5 h-5 ${card.color}`} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className={`text-3xl font-bold ${card.color}`}>{card.value}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>ステータス別記事数</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(Object.keys(STATUS_LABELS) as ArticleStatus[]).map((status) => (
                <div key={status} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {STATUS_LABELS[status]}
                  </span>
                  <span className="text-sm font-semibold">
                    {stats[status] || 0}件
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>最近のカテゴリ</CardTitle>
          </CardHeader>
          <CardContent>
            {categoriesData && categoriesData.length > 0 ? (
              <div className="space-y-3">
                {categoriesData.slice(0, 5).map((category) => (
                  <div key={category.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FolderOpen className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium">{category.name}</span>
                    </div>
                    <span className="text-xs text-gray-500">{category.slug}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">カテゴリがありません</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
