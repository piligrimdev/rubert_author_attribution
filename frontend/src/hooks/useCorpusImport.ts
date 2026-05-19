import { useMutation, useQueryClient } from "@tanstack/react-query";
import { importCorpusCsv } from "@/api/authorsApi";
import type { CorpusImportTaskStatus } from "@/types/corpusImport";
import type { AxiosError } from "axios";

const AUTHORS_KEY = ["authors"] as const;

export type CorpusImportVariables = {
  file: File;
  onProgress?: (percent: number) => void;
};

export function useCorpusImport() {
  const qc = useQueryClient();

  return useMutation<CorpusImportTaskStatus, AxiosError, CorpusImportVariables>({
    mutationFn: ({ file, onProgress }) => importCorpusCsv(file, onProgress),
    onSuccess: () => qc.invalidateQueries({ queryKey: AUTHORS_KEY }),
  });
}
