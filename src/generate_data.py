"""Generate a raw Iris dataset for local pipeline experiments."""
from pathlib import Path

from sklearn.datasets import load_iris

output_path = Path("data/raw/iris_v1.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

iris = load_iris(as_frame=True)
df = iris.frame
df.to_csv(output_path, index=False)
print(f"Saved {len(df)} rows to {output_path}")
