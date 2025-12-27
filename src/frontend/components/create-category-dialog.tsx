'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
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
import { categoriesApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Plus } from 'lucide-react';

interface CreateCategoryDialogProps {
  children?: React.ReactNode;
}

export function CreateCategoryDialog({ children }: CreateCategoryDialogProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: { name: string; slug: string }) =>
      categoriesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast({ title: 'カテゴリを作成しました' });
      setOpen(false);
      setName('');
      setSlug('');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 'カテゴリの作成に失敗しました';
      toast({
        title: 'エラー',
        description: errorMessage,
        variant: 'destructive'
      });
    },
  });

  const handleNameChange = (value: string) => {
    setName(value);
    // 名前からスラッグを自動生成（簡易版）
    if (!slug || slug === generateSlug(name)) {
      setSlug(generateSlug(value));
    }
  };

  const generateSlug = (text: string): string => {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, '-') // 英数字以外をハイフンに変換
      .replace(/-+/g, '-') // 連続するハイフンを1つに
      .replace(/^-+|-+$/g, ''); // 前後のハイフンを削除
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !slug.trim()) {
      toast({ title: '名前とスラッグを入力してください', variant: 'destructive' });
      return;
    }
    // スラッグのバリデーション（半角英小文字・数字・ハイフンのみ）
    if (!/^[a-z0-9-]+$/.test(slug.trim())) {
      toast({
        title: 'スラッグの形式が正しくありません',
        description: '半角英小文字・数字・ハイフンのみ使用できます',
        variant: 'destructive'
      });
      return;
    }
    createMutation.mutate({ name: name.trim(), slug: slug.trim() });
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
          <DialogTitle>カテゴリを作成</DialogTitle>
          <DialogDescription>
            新しいカテゴリを作成します。名前とスラッグを入力してください。
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">名前</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => handleNameChange(e.target.value)}
                placeholder="例: テクノロジー"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="slug">スラッグ</Label>
              <Input
                id="slug"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder="例: technology"
              />
              <p className="text-xs text-gray-500">
                URL表示用の識別子（半角英小文字・数字・ハイフンのみ）
              </p>
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
