import pandas as pd

from ECHA.ESAloaderAPI import ESAloaderAPI
from inventory_webdb import result_df_to_wide_dict


def main():
    exid = "ZOO_BL45XU_admin45_260428_5"

    esa = ESAloaderAPI(exid)

    print("=== prep ===")
    esa.prep()

    print("username =", esa.get_username())

    print("=== getSamplePin ===")
    samplepin_df = esa.getSamplePin()

    print(samplepin_df.columns.tolist())
    print(samplepin_df.head())

    if len(samplepin_df) == 0:
        print("No sample pin found")
        return

    first_row = samplepin_df.iloc[0]

    zoo_samplepin_id = first_row["id"]

    print("samplepin columns:")
    print(samplepin_df.columns.tolist())
    
    print("first_row:")
    print(first_row.to_dict())
    
    zoo_samplepin_id = first_row["id"]
    print("zoo_samplepin_id =", zoo_samplepin_id)

    print()
    print("target pin:")
    print("zoo_samplepin_id =", zoo_samplepin_id)

    print()
    print("=== getCond ===")
    cond_dict = esa.getCond(zoo_samplepin_id)

    print("cond keys:")
    print(sorted(cond_dict.keys()))

    print()
    print("=== getResult ===")
    result_df = esa.getResult(zoo_samplepin_id)

    print(result_df.columns.tolist())
    print(result_df.head())

    print()
    print("=== wide dict ===")
    result_dict = result_df_to_wide_dict(result_df)

    for k in sorted(result_dict.keys()):
        print(f"{k}: {result_dict[k]}")


if __name__ == "__main__":
    main()
