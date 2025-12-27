'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5分間はキャッシュを新鮮とみなす
            gcTime: 10 * 60 * 1000, // 10分間メモリにキャッシュを保持
            refetchOnWindowFocus: false,
            refetchOnMount: false, // マウント時に自動再取得しない
            retry: 1, // リトライ回数を減らして高速化
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
