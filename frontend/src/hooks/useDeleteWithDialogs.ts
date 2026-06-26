import { useState, useCallback } from "react";
import { getApiErrorDetail, isForbiddenError } from "@/utils/apiError";
import { strings } from "@/i18n/strings";

interface UseDeleteWithDialogsOptions<T> {
  deleteFn: (target: T) => Promise<void>;
  confirmTitle: string;
  getConfirmMessage: (target: T) => string;
  forbiddenFallback: string;
  onSuccess?: (target: T) => void;
}

export function useDeleteWithDialogs<T>({
  deleteFn,
  confirmTitle,
  getConfirmMessage,
  forbiddenFallback,
  onSuccess,
}: UseDeleteWithDialogsOptions<T>) {
  const [target, setTarget] = useState<T | null>(null);
  const [forbiddenMessage, setForbiddenMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const requestDelete = useCallback((item: T) => {
    setErrorMessage(null);
    setTarget(item);
  }, []);

  const cancelDelete = useCallback(() => {
    if (!isDeleting) setTarget(null);
  }, [isDeleting]);

  const closeForbidden = useCallback(() => setForbiddenMessage(null), []);

  const confirmDelete = useCallback(async () => {
    if (!target) return;
    setIsDeleting(true);
    setErrorMessage(null);
    try {
      await deleteFn(target);
      const deleted = target;
      setTarget(null);
      onSuccess?.(deleted);
    } catch (err) {
      if (isForbiddenError(err)) {
        setTarget(null);
        setForbiddenMessage(getApiErrorDetail(err, forbiddenFallback));
      } else {
        setErrorMessage(getApiErrorDetail(err, strings.dialogs.deleteFailed));
      }
    } finally {
      setIsDeleting(false);
    }
  }, [target, deleteFn, forbiddenFallback, onSuccess]);

  return {
    requestDelete,
    cancelDelete,
    confirmDelete,
    confirmTitle,
    confirmMessage: target ? getConfirmMessage(target) : "",
    forbiddenMessage,
    closeForbidden,
    errorMessage,
    clearError: () => setErrorMessage(null),
    isDeleting,
    isConfirmOpen: target !== null,
    isForbiddenOpen: forbiddenMessage !== null,
  };
}
