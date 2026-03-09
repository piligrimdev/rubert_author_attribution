import hashlib
import pandas as pd
from razdel import sentenize


def split_into_chunks(text: str, tokenizer,
                      chunk_size: int = 150,
                      sentence_overlap: int = 1,
                      min_chunk_tokens: int | None = None) -> list[str]:
    """
    Режем текст на чанки так, чтобы:
      - каждый чанк начинался с начала предложения и заканчивался концом предложения;
      - внутри чанка может быть несколько предложений;
      - суммарная длина чанка в токенах <= chunk_size;
      - соседние чанки перекрываются на `sentence_overlap` последних предложений
        (аналог бывшего stride, только на уровне предложений).

    min_chunk_tokens — отбрасываем слишком короткие хвосты (по умолчанию chunk_size // 2).
    """
    if min_chunk_tokens is None:
        min_chunk_tokens = chunk_size // 2

    # 1) Разбиваем на предложения и сразу считаем длину каждого в токенах.
    sentences = [s.text for s in sentenize(text)]
    sent_token_lens = [
        len(tokenizer.encode(s, add_special_tokens=False)) for s in sentences
    ]

    chunks: list[str] = []
    i = 0
    n = len(sentences)

    while i < n:
        # 2) Жадно набираем предложения, пока влезают в chunk_size.
        cur_len = 0
        j = i
        while j < n and cur_len + sent_token_lens[j] <= chunk_size:
            cur_len += sent_token_lens[j]
            j += 1

        if j == i:
            # Одно предложение не влезает в chunk_size целиком.
            # Варианта два: либо жёстко обрезать его по токенам (теряем "чистую" границу),
            # либо пропустить. Выбираем обрезку — лучше иметь чанк, чем потерять текст.
            ids = tokenizer.encode(sentences[i], add_special_tokens=False)[:chunk_size]
            chunks.append(tokenizer.decode(ids, skip_special_tokens=True))
            i += 1
            continue

        # 3) Склеиваем предложения [i, j) в один чанк.
        chunk_text = " ".join(sentences[i:j]).strip()
        if cur_len >= min_chunk_tokens or not chunks:
            # не добавляем слишком короткий хвост в самом конце, но всегда
            # гарантируем хотя бы один чанк на входной текст
            chunks.append(chunk_text)

        # 4) Сдвигаемся вперёд с перекрытием на sentence_overlap предложений.
        step = max(1, (j - i) - sentence_overlap)
        i += step

    return chunks


def split_text_to_chunks(df, tokenizer, chunk_size: int = 150, author_col='author', text_col='text'):
    result = []

    for author, group in df.groupby(author_col):
        for text in group[text_col]:
            chunks = split_into_chunks(text, tokenizer, chunk_size)
            source_id = hashlib.md5(text.encode('utf-8')).hexdigest()
            for chunk in chunks:
                result.append(
                    {
                        'author': author,
                        'text': chunk,
                        'source_id': source_id,
                    }
                )

    return pd.DataFrame(result)