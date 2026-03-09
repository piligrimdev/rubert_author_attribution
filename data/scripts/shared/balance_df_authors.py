import pandas as pd

def balance_authors(df: pd.DataFrame,
                    author_col: str = 'author',
                    min_fragments: int = 50,
                    max_fragments: int = 500,
                    random_state: int = 42) -> pd.DataFrame:
    balanced_parts = []
    excluded_authors = []

    for author, group in df.groupby(author_col):
        n = len(group)

        if n < min_fragments:
            excluded_authors.append((author, n))
            continue

        if n > max_fragments:
            group = group.sample(n=max_fragments, random_state=random_state)

        balanced_parts.append(group)

    if excluded_authors:
        print(f"Excluded authors:")
        for author, count in excluded_authors:
            print(f"\t{author}: {count} chunks")

    balanced_df = pd.concat(balanced_parts, ignore_index=True)

    print(f"Balanced authors: {balanced_df['author'].nunique()}")

    return balanced_df