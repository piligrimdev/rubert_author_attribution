import io
import structlog
import pandas as pd

logger = structlog.get_logger(__name__)

class CorpusCsvParseError(ValueError):
    pass


class CorpusCsvParseService:
    """Валидация файла перед обработкой"""

    def prepare_dataframe(self, raw: bytes) -> pd.DataFrame:
        if not raw:
            logger.error("csv_parsing.prepare_dataframe.file_is_empty")
            raise CorpusCsvParseError("Empty file")
        try:
            df = pd.read_csv(io.BytesIO(raw))
        except Exception as exc:
            logger.error("csv_parsing.prepare_dataframe.file_is_invalid", error=exc)
            raise CorpusCsvParseError(f"Invalid CSV: {exc}") from exc


        missing = {"author", "text", 'source_type'} - set(df.columns)
        if missing:
            error_text = ("CSV must contain columns author and text; missing: "
                + ", ".join(sorted(missing))
            )
            logger.error("csv_parsing.prepare_dataframe.file_is_invalid", error=error_text)
            raise CorpusCsvParseError(error_text)

        logger.info("csv_parsing.prepare_dataframe.file_validated")
        return df
