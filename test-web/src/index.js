// src/index.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// (선택) 개발 중 디버깅용
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,   // 5분 동안 신선
      gcTime: 30 * 60 * 1000,     // 캐시 보관 시간(v5)
      refetchOnWindowFocus: false,
    },
  },
});

const container = document.getElementById('root'); // public/index.html의 <div id="root">
if (!container) throw new Error('Root element #root not found');

const root = createRoot(container);
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {/* <ReactQueryDevtools initialIsOpen={false} /> */}
    </QueryClientProvider>
  </React.StrictMode>
);
