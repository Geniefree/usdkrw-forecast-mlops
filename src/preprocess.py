from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine


TICKERS = {
    "BTC": "BTC-USD",
    "KRW": "KRW=X",
    "JPY": "JPY=X",
    "WTI": "CL=F",
    "GOLD": "GC=F",
    "DXY": "DX-Y.NYB",
}


def collect_and_preprocess():
    now_et = datetime.now(ZoneInfo("America/New_York"))
    start_et = now_et - timedelta(hours=24)

    processed_each = {}

    for name, ticker in TICKERS.items():
        df = yf.download(
            ticker,
            start=start_et,
            end=now_et,
            interval="1m",
            progress=False,
        )

        df = df[["Close"]].copy()
        df.columns = [name]
        df.index = df.index.tz_convert("UTC")
        df = df.sort_index()

        processed_each[name] = df

    start_time = min(df.index.min() for df in processed_each.values())
    end_time = max(df.index.max() for df in processed_each.values())

    base_index = pd.date_range(
        start=start_time,
        end=end_time,
        freq="1min",
        tz="UTC",
    )

    final_parts = {}

    for name, df in processed_each.items():
        reindexed = df.reindex(base_index)
        reindexed.index.name = "timestamp"

        interpolated = reindexed.interpolate(method="linear")
        final_parts[name] = interpolated

    final_df = pd.concat(final_parts.values(), axis=1)
    final_df = final_df.tail(1440)

    return final_df


def save_to_csv(final_df):
    final_df.to_csv("data/processed/market_data_1m_24h_interpolated.csv")


def save_to_postgres(final_df):
    engine = create_engine(
        "postgresql://admin:admin@localhost:5432/marketdb"
    )

    final_df.to_sql(
        name="latest_24h_market_data_1m",
        con=engine,
        if_exists="replace",
        index=True,
    )


if __name__ == "__main__":
    final_df = collect_and_preprocess()

    print(final_df.shape)
    print(final_df.isnull().sum())

    save_to_csv(final_df)
    save_to_postgres(final_df)

    print("CSV 및 PostgreSQL 저장 완료")