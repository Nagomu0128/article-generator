'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { articlesApi, categoriesApi, wordpressApi } from '@/lib/api';
import { STATUS_LABELS, STATUS_COLORS, ArticleStatus } from '@/types';
import { useToast } from '@/hooks/use-toast';
import {
  ArrowLeft,
  Play,
  RefreshCw,
  Edit,
  Save,
  FileText,
  ExternalLink,
  Trash2,
  Globe,
} from 'lucide-react';
import Link from 'next/link';

export default function ArticleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const articleId = params.id as string;

  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');
  const [editedContent, setEditedContent] = useState('');

  // 記事データ取得
  const { data: article, isLoading } = useQuery({
    queryKey: ['article', articleId],
    queryFn: async () => {
      const response = await articlesApi.get(articleId);
      return response.data;
    },
  });

  // カテゴリデータ取得
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await categoriesApi.list();
      return response.data;
    },
  });

  // 編集モード開始時にデータをセット
  const handleStartEdit = () => {
    setEditedTitle(article?.title || '');
    setEditedContent(article?.content || '');
    setIsEditing(true);
  };

  // 記事生成
  const generateMutation = useMutation({
    mutationFn: () => articlesApi.generate(articleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
      toast({ title: '記事生成を開始しました' });
    },
    onError: (error: any) => {
      toast({
        title: '記事生成に失敗しました',
        description: error?.response?.data?.detail || error?.message,
        variant: 'destructive',
      });
    },
  });

  // 記事再生成
  const regenerateMutation = useMutation({
    mutationFn: () => articlesApi.regenerate(articleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
      toast({ title: '記事の再生成を開始しました' });
    },
    onError: (error: any) => {
      toast({
        title: '記事の再生成に失敗しました',
        description: error?.response?.data?.detail || error?.message,
        variant: 'destructive',
      });
    },
  });

  // 記事更新
  const updateMutation = useMutation({
    mutationFn: (data: { title?: string; content?: string }) =>
      articlesApi.update(articleId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
      setIsEditing(false);
      toast({ title: '記事を更新しました' });
    },
    onError: (error: any) => {
      toast({
        title: '記事の更新に失敗しました',
        description: error?.response?.data?.detail || error?.message,
        variant: 'destructive',
      });
    },
  });

  // WordPress下書き保存
  const draftMutation = useMutation({
    mutationFn: () => wordpressApi.draft(articleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
      toast({ title: 'WordPressに下書きを保存しました' });
    },
    onError: (error: any) => {
      toast({
        title: 'WordPress下書き保存に失敗しました',
        description: error?.response?.data?.detail || error?.message,
        variant: 'destructive',
      });
    },
  });

  // WordPress公開
  const publishMutation = useMutation({
    mutationFn: () => wordpressApi.publish(articleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
      toast({ title: 'WordPressに公開しました' });
    },
    onError: (error: any) => {
      toast({
        title: 'WordPress公開に失敗しました',
        description: error?.response?.data?.detail || error?.message,
        variant: 'destructive',
      });
    },
  });

  // 記事削除
  const deleteMutation = useMutation({
    mutationFn: () => articlesApi.delete(articleId),
    onSuccess: () => {
      toast({ title: '記事を削除しました' });
      router.push('/articles');
    },
    onError: (error: any) => {
      toast({
        title: '記事の削除に失敗しました',
        description: error?.response?.data?.detail || error?.message,
        variant: 'destructive',
      });
    },
  });

  const handleSave = () => {
    updateMutation.mutate({
      title: editedTitle,
      content: editedContent,
    });
  };

  const handleDelete = () => {
    if (confirm('本当にこの記事を削除しますか？')) {
      deleteMutation.mutate();
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">読み込み中...</p>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">記事が見つかりません</p>
        <Link href="/articles">
          <Button variant="outline" className="mt-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            記事一覧に戻る
          </Button>
        </Link>
      </div>
    );
  }

  const category = categories?.find((c) => c.id === article.category_id);

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/articles">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              戻る
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">記事詳細</h1>
            <p className="text-gray-500 mt-1">{article.keyword}</p>
          </div>
        </div>
        <div className="flex gap-2">
          {article.status === 'pending' && (
            <Button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
            >
              <Play className="w-4 h-4 mr-2" />
              {generateMutation.isPending ? '生成中...' : '記事を生成'}
            </Button>
          )}
          {article.content && article.status !== 'pending' && (
            <Button
              variant="outline"
              onClick={() => regenerateMutation.mutate()}
              disabled={regenerateMutation.isPending}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              {regenerateMutation.isPending ? '再生成中...' : '再生成'}
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* メインコンテンツ */}
        <div className="lg:col-span-2 space-y-6">
          {/* 記事情報 */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>記事情報</CardTitle>
              {!isEditing && article.content && (
                <Button variant="outline" size="sm" onClick={handleStartEdit}>
                  <Edit className="w-4 h-4 mr-2" />
                  編集
                </Button>
              )}
              {isEditing && (
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(false)}
                  >
                    キャンセル
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={updateMutation.isPending}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    保存
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  キーワード
                </label>
                <p className="mt-1 text-gray-900">{article.keyword}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  タイトル
                </label>
                {isEditing ? (
                  <Textarea
                    value={editedTitle}
                    onChange={(e) => setEditedTitle(e.target.value)}
                    className="mt-1"
                    rows={2}
                  />
                ) : (
                  <p className="mt-1 text-gray-900">
                    {article.title || '未生成'}
                  </p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  カテゴリ
                </label>
                <p className="mt-1 text-gray-900">{category?.name || '-'}</p>
              </div>
            </CardContent>
          </Card>

          {/* 記事本文 */}
          <Card>
            <CardHeader>
              <CardTitle>記事本文</CardTitle>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <Textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="min-h-[400px] font-mono text-sm"
                />
              ) : article.content ? (
                <div
                  className="prose max-w-none"
                  dangerouslySetInnerHTML={{ __html: article.content }}
                />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  記事が生成されていません
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* サイドバー */}
        <div className="space-y-6">
          {/* ステータス */}
          <Card>
            <CardHeader>
              <CardTitle>ステータス</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  現在のステータス
                </label>
                <div className="mt-2">
                  <Badge className={STATUS_COLORS[article.status as ArticleStatus]}>
                    {STATUS_LABELS[article.status as ArticleStatus]}
                  </Badge>
                </div>
              </div>
              <Separator />
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">作成日時</span>
                  <span className="text-gray-900">
                    {new Date(article.created_at).toLocaleString('ja-JP')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">更新日時</span>
                  <span className="text-gray-900">
                    {new Date(article.updated_at).toLocaleString('ja-JP')}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* WordPress情報 */}
          {(article.wp_post_id || article.wp_url) && (
            <Card>
              <CardHeader>
                <CardTitle>WordPress情報</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {article.wp_post_id && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      投稿ID
                    </label>
                    <p className="mt-1 text-gray-900">{article.wp_post_id}</p>
                  </div>
                )}
                {article.wp_url && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      公開URL
                    </label>
                    <a
                      href={article.wp_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 text-blue-600 hover:underline flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      リンクを開く
                    </a>
                  </div>
                )}
                {article.wp_published_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      公開日時
                    </label>
                    <p className="mt-1 text-gray-900">
                      {new Date(article.wp_published_at).toLocaleString('ja-JP')}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* アクション */}
          <Card>
            <CardHeader>
              <CardTitle>アクション</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {article.content && article.status !== 'published' && (
                <>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => draftMutation.mutate()}
                    disabled={draftMutation.isPending}
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    {draftMutation.isPending ? '保存中...' : 'WordPressに下書き保存'}
                  </Button>
                  <Button
                    className="w-full"
                    onClick={() => publishMutation.mutate()}
                    disabled={publishMutation.isPending}
                  >
                    <Globe className="w-4 h-4 mr-2" />
                    {publishMutation.isPending ? '公開中...' : 'WordPressに公開'}
                  </Button>
                </>
              )}
              <Separator />
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                {deleteMutation.isPending ? '削除中...' : '記事を削除'}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
