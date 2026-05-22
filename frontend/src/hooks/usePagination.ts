import { useState, useMemo, useCallback } from 'react';

interface UsePaginationReturn {
  page: number;
  totalPages: number;
  setPage: (page: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  canNext: boolean;
  canPrev: boolean;
}

export function usePagination(total: number, pageSize: number): UsePaginationReturn {
  const [page, setPageInternal] = useState(1);

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(total / pageSize)),
    [total, pageSize]
  );

  const setPage = useCallback(
    (p: number) => {
      setPageInternal(Math.max(1, Math.min(p, totalPages)));
    },
    [totalPages]
  );

  const nextPage = useCallback(() => {
    setPageInternal((prev) => Math.min(prev + 1, totalPages));
  }, [totalPages]);

  const prevPage = useCallback(() => {
    setPageInternal((prev) => Math.max(prev - 1, 1));
  }, []);

  const canNext = page < totalPages;
  const canPrev = page > 1;

  return { page, totalPages, setPage, nextPage, prevPage, canNext, canPrev };
}
