import zipfile

import gdown
import pandas as pd

from src.config import (
    GOOGLE_DRIVE_FILE_ID,
    RAW_DATA_DIR,
    TRAIN_FILE,
    TEST_FILE,
    ZIP_FILE,
    TARGET_COL,
    TARGET_MAPPING,
)


def download_dataset(force_download: bool = False) -> None:
    """
    Descarga y extrae el dataset si todavía no existe.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if (
        TRAIN_FILE.exists()
        and TEST_FILE.exists()
        and not force_download
    ):
        print("Dataset ya disponible.")
        return

    url = (
        "https://drive.google.com/uc"
        f"?id={GOOGLE_DRIVE_FILE_ID}"
    )

    print("Descargando dataset...")

    gdown.download(
        url,
        str(ZIP_FILE),
        quiet=False,
    )

    print("Extrayendo dataset...")

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(RAW_DATA_DIR)

    print("Dataset descargado correctamente.")


def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga train.csv y test.csv.
    """

    download_dataset()

    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)

    return train_df, test_df


def clean_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Realiza la limpieza básica utilizada
    en la notebook original.
    """

    df = df.copy()

    df = df.drop(
        columns=["Unnamed: 0", "id"],
        errors="ignore",
    )

    return df


def encode_target(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convierte satisfaction a 0/1.
    """

    df = df.copy()

    df[TARGET_COL] = (
        df[TARGET_COL]
        .map(TARGET_MAPPING)
    )

    return df


def load_and_prepare_data():
    """
    Pipeline completo de carga y limpieza.
    """

    train_df, test_df = load_dataset()

    train_df = clean_dataset(train_df)
    test_df = clean_dataset(test_df)

    train_df = encode_target(train_df)
    test_df = encode_target(test_df)

    return train_df, test_df


if __name__ == "__main__":

    train_df, test_df = load_and_prepare_data()

    print("Train:", train_df.shape)
    print("Test:", test_df.shape)

    print("\nTarget train:")
    print(
        train_df[TARGET_COL]
        .value_counts()
    )