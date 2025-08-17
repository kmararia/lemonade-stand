""" """

from banana_stand.app_config import AppConfig
from banana_stand.data_prep import Statement
from banana_stand.data_prep import Transactions
from banana_stand.data_prep import read_pdfplumber


def main():
    """
    Main application function
    """

    # Set up session configurations
    run_config = AppConfig()

    # Load all user transactions
    transactions = Transactions(
        statements_list=[
            Statement(file_path=file, read_func=read_pdfplumber)
            for file in (run_config.statement_dir).glob("*.pdf")
        ]
    )

    # # Validation transactions
    # vldtn_transactions = Transactions(
    #     statements_list=[
    #         Statement(
    #             file_path=file,
    #             read_func=read_pymullm
    #         )
    #         for file in (run_config.statement_dir).glob("*.pdf")
    #     ]
    # )

    # missing = transactions.data.join(
    #     vldtn_transactions.data,
    #     on=transactions.data.columns,
    #     how="anti"
    # )

    # print(missing)
    print(transactions.data)

    # Confirm if this is a simulation run
    if run_config.simulation:
        pass


if __name__ == "__main__":
    main()
