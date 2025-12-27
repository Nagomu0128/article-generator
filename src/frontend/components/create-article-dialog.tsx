'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { categoriesApi, articlesApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Plus } from 'lucide-react';

interface CreateArticleDialogProps {
  children?: React.ReactNode;
}

export function CreateArticleDialog({ children }: CreateArticleDialogProps) {
  const [open, setOpen] = useState(false);
  const [categoryId, setCategoryId] = useState('');
  const [keyword, setKeyword] = useState('');
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await categoriesApi.list();
      return response.data;
    },
    staleTime: 30 * 60 * 1000, // カテゴリは30分間キャッシュ
  });

  const createMutation = useMutation({
    mutationFn: (data: { category_id: string; keyword: string }) =>
      articlesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      toast({ title: '記事を作成しました' });
      setOpen(false);
      setCategoryId('');
      setKeyword('');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || '記事の作成に失敗しました';
      toast({
        title: 'エラー',
        description: errorMessage,
        variant: 'destructive'
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!categoryId || !keyword.trim()) {
      toast({ title: 'カテゴリーとキーワードを入力してください', variant: 'destructive' });
      return;
    }
    createMutation.mutate({ category_id: categoryId, keyword: keyword.trim() });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            新規作成
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>記事を作成</DialogTitle>
          <DialogDescription>
            新しい記事を作成します。カテゴリーとキーワードを入力してください。
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="category">カテゴリー</Label>
              <Select value={categoryId} onValueChange={setCategoryId} disabled={categoriesLoading}>
                <SelectTrigger id="category">
                  <SelectValue placeholder={categories?.length === 0 ? "カテゴリーがありません" : "カテゴリーを選択"} />
                </SelectTrigger>
                <SelectContent>
                  {categories?.length === 0 ? (
                    <div className="px-2 py-6 text-center text-sm text-gray-500">
                      カテゴリーがありません。<br />
                      先にカテゴリーを作成してください。
                    </div>
                  ) : (
                    categories?.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="keyword">キーワード</Label>
              <Input
                id="keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="例: Next.js チュートリアル"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              キャンセル
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? '作成中...' : '作成'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
