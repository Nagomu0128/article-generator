'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { categoriesApi, sheetsApi } from '@/lib/api';
import { FolderOpen, ExternalLink, FileSpreadsheet } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CreateCategoryDialog } from '@/components/create-category-dialog';
import { LinkSheetDialog } from '@/components/link-sheet-dialog';
import { useToast } from '@/hooks/use-toast';

export default function CategoriesPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [creatingSheetId, setCreatingSheetId] = useState<string | null>(null);

  const { data: categoriesData, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await categoriesApi.list();
      return response.data;
    },
    staleTime: 30 * 60 * 1000, // カテゴリは30分間キャッシュ
  });

  const createSheetMutation = useMutation({
    mutationFn: (categoryId: string) => sheetsApi.create(categoryId),
    onMutate: (categoryId: string) => {
      setCreatingSheetId(categoryId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast({ title: 'スプレッドシートを作成しました' });
      setCreatingSheetId(null);
    },
    onError: (error: any) => {
      console.error('Sheet creation error:', error);
      const errorDetail = error?.response?.data?.detail;
      const errorMessage = typeof errorDetail === 'string'
        ? errorDetail
        : error?.message || 'スプレッドシートの作成に失敗しました';

      toast({
        title: 'スプレッドシート作成エラー',
        description: errorMessage,
        variant: 'destructive'
      });
      setCreatingSheetId(null);
    },
  });

  const categories = categoriesData || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">カテゴリ一覧</h1>
          <p className="text-gray-500 mt-1">全{categories.length}件のカテゴリ</p>
        </div>
        <CreateCategoryDialog />
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">読み込み中...</p>
        </div>
      ) : categories.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border">
          <p className="text-gray-500">カテゴリがありません</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((category) => (
            <Card key={category.id}>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <FolderOpen className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{category.name}</CardTitle>
                    <p className="text-sm text-gray-500">{category.slug}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Google Sheets:</span>
                    {category.sheet_url ? (
                      <a
                        href={category.sheet_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline flex items-center gap-1"
                      >
                        <ExternalLink className="w-3 h-3" />
                        開く
                      </a>
                    ) : (
                      <span className="text-gray-400">未作成</span>
                    )}
                  </div>
                  {category.sheets_synced_at && (
                    <div className="text-xs text-gray-500">
                      最終同期: {new Date(category.sheets_synced_at).toLocaleString('ja-JP')}
                    </div>
                  )}
                  <div className="pt-2">
                    {category.sheet_url ? (
                      <a
                        href={category.sheet_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button variant="outline" size="sm" className="w-full">
                          <FileSpreadsheet className="w-4 h-4 mr-2" />
                          スプレッドシートを開く
                        </Button>
                      </a>
                    ) : (
                      <div className="space-y-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full"
                          onClick={() => createSheetMutation.mutate(category.id)}
                          disabled={creatingSheetId === category.id}
                        >
                          <FileSpreadsheet className="w-4 h-4 mr-2" />
                          {creatingSheetId === category.id ? '作成中...' : 'スプレッドシート作成'}
                        </Button>
                        <LinkSheetDialog categoryId={category.id} categoryName={category.name} />
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
