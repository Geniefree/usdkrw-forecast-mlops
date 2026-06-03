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


def is_weekend_closed(ts):
    """
    FX/선물 주말 비활성 구간:
    금요일 22:00 UTC ~ 일요일 22:00 UTC 제외
    """
    ts = pd.Timestamp(ts).tz_convert("UTC")
    weekday = ts.weekday()  # 월=0, ..., 금=4, 토=5, 일=6
    hour = ts.hour

    if weekday == 5:
        return True
    if weekday == 4 and hour >= 22:
        return True
    if weekday == 6 and hour < 22:
        return True

    return False


def make_valid_rolling_index(end_time=None, periods=1440):
    """
    end_time 기준으로 뒤로 1분씩 이동하면서,
    주말 비활성 구간을 제외한 최근 유효 1440분 timestamp 생성
    """
    if end_time is None:
        end_time = pd.Timestamp.now(tz="UTC")
    else:
        end_time = pd.Timestamp(end_time).tz_convert("UTC")

    valid_times = []
    cur = end_time.floor("min")

    while len(valid_times) < periods:
        if not is_weekend_closed(cur):
            valid_times.append(cur)
        cur -= pd.Timedelta(minutes=1)

    valid_times = sorted(valid_times)
    return pd.DatetimeIndex(valid_times, name="timestamp")


def collect_and_preprocess():
    now_et = datetime.now(ZoneInfo("America/New_York"))

    # 주말 비활성 구간을 건너뛸 수 있도록 넉넉하게 5일치 요청
    start_et = now_et - timedelta(days=5)

    raw_each = {}

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

        raw_each[name] = df

    # 주말 비활성 구간을 제외한 최근 유효 1440분 기준 timestamp 생성
    base_index = make_valid_rolling_index(periods=1440)

    final_parts = {}

    for name, df in raw_each.items():
        reindexed = df.reindex(base_index)
        reindexed.index.name = "timestamp"

        interpolated = reindexed.interpolate(method="linear")
        final_parts[name] = interpolated

    final_df = pd.concat(final_parts.values(), axis=1)

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