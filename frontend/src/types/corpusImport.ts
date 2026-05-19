export type CorpusCsvImportResult = {
  added: number;
  skipped_empty: number;
  errors: number;
};

export type StartCorpusImportTaskResponse = {
  task_id: string;
};

export type CorpusImportTaskStatus = {
  task_id: string;
  status: string;
  progress?: number | null;
  result?: CorpusCsvImportResult | null;
  error?: string | null;
};
