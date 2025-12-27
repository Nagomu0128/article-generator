'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Link } from 'lucide-react';
import { sheetsApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface LinkSheetDialogProps {
  categoryId: string;
  categoryName: string;
}

export function LinkSheetDialog({ categoryId, categoryName }: LinkSheetDialogProps) {
  const [open, setOpen] = useState(false);
  const [sheetUrl, setSheetUrl] = useState('');
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const linkSheetMutation = useMutation({
    mutationFn: ({ sheetId, sheetUrl }: { sheetId: string; sheetUrl: string }) =>
      sheetsApi.link(categoryId, sheetId, sheetUrl),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast({ title: 'スプレッドシートをリンクしました' });
      setOpen(false);
      setSheetUrl('');
    },
    onError: (error: any) => {
      const errorDetail = error?.response?.data?.detail;
      const errorMessage =
        typeof errorDetail === 'string'
          ? errorDetail
          : error?.message || 'スプレッドシートのリンクに失敗しました';

      toast({
        title: 'エラー',
        description: errorMessage,
        variant: 'destructive',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // URLからスプレッドシートIDを抽出
    const match = sheetUrl.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
    if (!match) {
      toast({
        title: 'エラー',
        description: '正しいGoogle SheetsのURLを入力してください',
        variant: 'destructive',
      });
      return;
    }

    const sheetId = match[1];
    linkSheetMutation.mutate({ sheetId, sheetUrl });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="w-full">
          <Link className="w-4 h-4 mr-2" />
          手動でリンク
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>スプレッドシートをリンク</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="category">カテゴリ</Label>
            <Input id="category" value={categoryName} disabled />
          </div>
          <div>
            <Label htmlFor="sheetUrl">スプレッドシートURL</Label>
            <Input
              id="sheetUrl"
              value={sheetUrl}
              onChange={(e) => setSheetUrl(e.target.value)}
              placeholder="https://docs.google.com/spreadsheets/d/..."
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Google Sheetsで作成したスプレッドシートのURLを貼り付けてください
            </p>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
            <p className="font-semibold mb-2">事前準備:</p>
            <ol className="list-decimal list-inside space-y-1 text-gray-700">
              <li>Google Sheetsで新しいスプレッドシートを作成</li>
              <li>1行目にヘッダー（KW, 記事タイトル, ステータス等）を追加</li>
              <li>
                サービスアカウント（
                <code className="bg-white px-1 py-0.5 rounded text-xs">
                  article-generator-sa@article-generator-482515.iam.gserviceaccount.com
                </code>
                ）を「編集者」として共有
              </li>
            </ol>
          </div>
          <div className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              キャンセル
            </Button>
            <Button type="submit" disabled={linkSheetMutation.isPending}>
              {linkSheetMutation.isPending ? 'リンク中...' : 'リンク'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
