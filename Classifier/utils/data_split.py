# utils/data_split.py
import numpy as np
from sklearn.model_selection import train_test_split

def train_test_split_by_title(
    df,
    text_col="emergency_title",
    label_col="emergency_type",
    test_size=0.2,
    random_state=42,
):
    """
    Split dataframe so that no unique text/title appears in both train and test.
    Returns: X_train, X_test, y_train, y_test (as pandas Series)
    """
    # Unique titles (preserve order randomness by using numpy array)
    unique_titles = np.array(df[text_col].dropna().unique())
    if len(unique_titles) == 0:
        raise ValueError(f"No unique titles found in column '{text_col}'")

    train_titles, test_titles = train_test_split(
        unique_titles, test_size=test_size, random_state=random_state
    )

    train_df = df[df[text_col].isin(train_titles)].copy()
    test_df = df[df[text_col].isin(test_titles)].copy()

    # Quick diagnostics
    print("=== SAFE SPLIT CHECK ===")
    print(f"Total unique titles: {len(unique_titles)}")
    print(f"Train titles: {len(train_titles)}, Test titles: {len(test_titles)}")
    print(f"Train samples: {len(train_df)}, Test samples: {len(test_df)}")
    print(f"Overlap in titles (should be 0): {len(set(train_titles) & set(test_titles))}")
    print("=" * 40)

    X_train, y_train = train_df[text_col], train_df[label_col]
    X_test, y_test = test_df[text_col], test_df[label_col]

    return X_train, X_test, y_train, y_test
