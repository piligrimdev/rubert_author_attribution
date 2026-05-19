import io

import pandas as pd


class CorpusCsvParseError(ValueError):
    pass


class CorpusCsvParseService:
    """Валидация файла перед обработкой"""

    def prepare_dataframe(self, raw: bytes) -> pd.DataFrame:
        if not raw:
            raise CorpusCsvParseError("Empty file")
        try:
            df = pd.read_csv(io.BytesIO(raw))
        except Exception as exc:
            raise CorpusCsvParseError(f"Invalid CSV: {exc}") from exc


        missing = {"author", "text", 'source_type'} - set(df.columns)
        if missing:
            raise CorpusCsvParseError(
                "CSV must contain columns author and text; missing: "
                + ", ".join(sorted(missing))
            )

        return df
