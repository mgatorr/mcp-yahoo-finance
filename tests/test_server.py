from unittest.mock import MagicMock, patch

import pytest
from mcp.types import Tool

from mcp_yahoo_finance.server import YahooFinance
from mcp_yahoo_finance.utils import generate_tool


@pytest.fixture
def client_tools() -> list[Tool]:
    yf = YahooFinance()
    return [
        generate_tool(yf.get_current_stock_price),
        generate_tool(yf.get_stock_price_by_date),
        generate_tool(yf.get_stock_price_date_range),
        generate_tool(yf.get_historical_stock_prices),
        generate_tool(yf.get_dividends),
        generate_tool(yf.get_income_statement),
        generate_tool(yf.get_cashflow),
        generate_tool(yf.get_earning_dates),
        generate_tool(yf.get_news),
        generate_tool(yf.get_recommendations),
        generate_tool(yf.get_option_expiration_dates),
        generate_tool(yf.get_option_chain),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name",
    [
        "get_current_stock_price",
        "get_stock_price_by_date",
        "get_stock_price_date_range",
        "get_historical_stock_prices",
        "get_dividends",
        "get_income_statement",
        "get_cashflow",
        "get_earning_dates",
        "get_news",
        "get_recommendations",
        "get_option_expiration_dates",
        "get_option_chain",
    ],
)
async def test_list_tools(client_tools: list[Tool], tool_name) -> None:
    tool_names = [tool.name for tool in client_tools]
    assert tool_name in tool_names


@pytest.mark.parametrize(
    "symbol, date, expected_price",
    [
        ("AAPL", "2025-01-02", "243.5822"),
        ("GOOG", "2025-01-03", "142.5683"),
        ("META", "2025-01-03", "594.8756"),
    ],
)
def test_get_stock_price_by_date(symbol, date, expected_price):
    import pandas as pd

    from mcp_yahoo_finance.server import YahooFinance

    mock_df = pd.DataFrame({"Close": [float(expected_price)]})
    mock_df.index = pd.DatetimeIndex(["2025-01-02"])

    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_df
        mock_ticker_class.return_value = mock_ticker

        yf = YahooFinance()
        result = yf.get_stock_price_by_date(symbol, date)

        assert result == expected_price


def _mock_ticker(*, info=None, history_df=None):
    """Build a mocked yfinance Ticker.

    info: value returned by ``.info`` (dict or None).
    history_df: DataFrame returned by ``.history(...)``; defaults to empty.
    """
    import pandas as pd

    ticker = MagicMock()
    ticker.info = info if info is not None else {}
    ticker.history.return_value = (
        history_df if history_df is not None else pd.DataFrame()
    )
    return ticker


def test_current_price_normal_ticker_returns_formatted_price():
    """UNH: a liquid ticker with a regularMarketPrice formats to 4 decimals."""
    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = _mock_ticker(
            info={"regularMarketPrice": 512.3}
        )

        yf = YahooFinance()
        result = yf.get_current_stock_price("UNH")

        assert result == "512.3000"


def test_current_price_numeric_string_does_not_crash():
    """A numeric value arriving as a string must be coerced, not crash on ':.4f'."""
    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = _mock_ticker(
            info={"regularMarketPrice": "512.3"}
        )

        yf = YahooFinance()
        result = yf.get_current_stock_price("UNH")

        assert result == "512.3000"


def test_current_price_illiquid_na_string_falls_back_to_last_close():
    """OD7C.DE: info has a truthy non-numeric 'N/A' (the reported crash case).

    Must NOT raise "Unknown format code 'f' for object of type 'str'"; instead
    fall back to the last available close from history.
    """
    import pandas as pd

    hist = pd.DataFrame({"Close": [float("nan"), 41.25, 41.80]})
    hist.index = pd.DatetimeIndex(["2026-05-26", "2026-05-27", "2026-05-28"])

    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = _mock_ticker(
            info={"regularMarketPrice": "N/A", "currentPrice": None},
            history_df=hist,
        )

        yf = YahooFinance()
        result = yf.get_current_stock_price("OD7C.DE")

        assert result == "41.8000"


def test_current_price_missing_field_falls_back_to_last_close():
    """OD7C.DE: info lacks both price fields -> use last non-NaN close."""
    import pandas as pd

    hist = pd.DataFrame({"Close": [40.0, float("nan")]})
    hist.index = pd.DatetimeIndex(["2026-05-27", "2026-05-28"])

    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = _mock_ticker(info={}, history_df=hist)

        yf = YahooFinance()
        result = yf.get_current_stock_price("OD7C.DE")

        assert result == "40.0000"


def test_current_price_no_data_returns_clear_message():
    """Nonexistent / dataless symbol: no price and no history -> clear message."""
    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = _mock_ticker(info={})

        yf = YahooFinance()
        result = yf.get_current_stock_price("NOPE.XX")

        assert result == "No price data available for NOPE.XX"


@pytest.mark.parametrize("symbol", ["UNH", "OD7C.DE", "NOPE.XX"])
def test_current_price_never_raises(symbol):
    """None of the three scenarios may raise an exception."""
    import pandas as pd

    scenarios = {
        "UNH": _mock_ticker(info={"regularMarketPrice": 512.3}),
        "OD7C.DE": _mock_ticker(
            info={"regularMarketPrice": "N/A"},
            history_df=pd.DataFrame(
                {"Close": [41.8]}, index=pd.DatetimeIndex(["2026-05-28"])
            ),
        ),
        "NOPE.XX": _mock_ticker(info={}),
    }
    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = scenarios[symbol]

        yf = YahooFinance()
        # Must not raise.
        result = yf.get_current_stock_price(symbol)
        assert isinstance(result, str) and result


def test_stock_price_by_date_nan_close_does_not_crash():
    """get_stock_price_by_date with a NaN close must not emit 'nan' or crash."""
    import pandas as pd

    mock_df = pd.DataFrame({"Close": [float("nan")]})
    mock_df.index = pd.DatetimeIndex(["2026-05-28"])

    with patch("mcp_yahoo_finance.server.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = _mock_ticker(history_df=mock_df)

        yf = YahooFinance()
        result = yf.get_stock_price_by_date("OD7C.DE", "2026-05-28")

        assert result.startswith("Error")


def test_coerce_float_handles_non_numeric():
    """The shared coercion helper returns None for non-numeric / missing input."""
    from mcp_yahoo_finance.utils import coerce_float

    assert coerce_float(512.3) == 512.3
    assert coerce_float("512.3") == 512.3
    assert coerce_float("N/A") is None
    assert coerce_float("") is None
    assert coerce_float(None) is None
    assert coerce_float(float("nan")) is None
