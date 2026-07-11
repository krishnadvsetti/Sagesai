import numpy as np
import pandas as pd


FEATURES = [
    "failed_logins",
    "login_hour",
    "request_rate",
    "unique_ips",
    "privilege_actions",
    "data_transfer_mb",
]


def generate_authentication_data(
    samples: int = 5000,
    random_state: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    normal_count = int(samples * 0.95)
    anomaly_count = samples - normal_count

    normal = pd.DataFrame(
        {
            "failed_logins": rng.poisson(1, normal_count),
            "login_hour": rng.normal(13, 4, normal_count).clip(0, 23),
            "request_rate": rng.normal(40, 12, normal_count).clip(1),
            "unique_ips": rng.poisson(2, normal_count) + 1,
            "privilege_actions": rng.poisson(0.3, normal_count),
            "data_transfer_mb": rng.lognormal(3, 0.7, normal_count),
            "label": 0,
        }
    )

    anomalies = pd.DataFrame(
        {
            "failed_logins": rng.integers(10, 60, anomaly_count),
            "login_hour": rng.choice([0, 1, 2, 3, 4, 23], anomaly_count),
            "request_rate": rng.uniform(150, 600, anomaly_count),
            "unique_ips": rng.integers(10, 60, anomaly_count),
            "privilege_actions": rng.integers(5, 30, anomaly_count),
            "data_transfer_mb": rng.uniform(500, 5000, anomaly_count),
            "label": 1,
        }
    )

    return (
        pd.concat([normal, anomalies], ignore_index=True)
        .sample(frac=1, random_state=random_state)
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    dataframe = generate_authentication_data()
    print(dataframe.head())
    print(dataframe["label"].value_counts())