import pandas as pd
from sklearn.preprocessing import StandardScaler

DATA_PATH = "data/raw/creditcard.csv"
OUTPUT_PATH = "data/processed/reference.csv"
SAMPLE_SIZE = 5000


def main():
    df = pd.read_csv(DATA_PATH)

    df = df.drop(columns=["Time"])

    scaler = StandardScaler()
    df["Amount"] = scaler.fit_transform(df[["Amount"]])

    frac = SAMPLE_SIZE / len(df)
    fraud = df[df["Class"] == 1].sample(frac=frac, random_state=42)
    legit = df[df["Class"] == 0].sample(frac=frac, random_state=42)
    reference = pd.concat([fraud, legit]).reset_index(drop=True)

    reference.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(reference)} rows to {OUTPUT_PATH}")
    print(f"Fraud cases: {reference['Class'].sum()} ({reference['Class'].mean()*100:.2f}%)")


if __name__ == "__main__":
    main()
