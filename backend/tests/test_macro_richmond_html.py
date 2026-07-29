"""Richmond HTML 采集器测试."""

import pytest

from app.collectors.macro_richmond_html import MacroRichmondHTMLCollector

HTML_CONTENT = b"""<html><body>
<table>
<tr><th>Date</th><th>Lower 16%</th><th>Median</th><th>Upper 84%</th></tr>
<tr><td>2023-03-31</td><td>1.10</td><td>1.50</td><td>1.90</td></tr>
<tr><td>2023-06-30</td><td>1.15</td><td>1.55</td><td>1.95</td></tr>
<tr><td>Notes: Data from Lubik-Matthes model.</td><td></td><td></td><td></td></tr>
</table>
</body></html>"""


@pytest.fixture
def lm_config():
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "source_code": "r-star-LM",
        "source_type": "html",
        "url": "https://www.richmondfed.org/research/national_economy/natural_rate_interest",
        "parse_config": {
            "table_index": 0,
            "skip_footnotes": True,
            "frequency": "quarterly",
            "columns": {"date": 0, "lower16": 1, "median": 2, "upper84": 3},
            "indicator_key": "r_star_lm",
            "value_column": "median",
            "country": "US",
        },
        "timeout_seconds": 30,
        "retry_max_attempts": 2,
    }


class TestRichmondHTML:
    """Richmond Fed HTML 解析测试."""

    async def test_parse_table(self, lm_config):
        collector = MacroRichmondHTMLCollector(lm_config)
        df = await collector.parse_raw(HTML_CONTENT)
        assert len(df) == 2
        assert df.iloc[0]["country"] == "US"
        assert df.iloc[0]["indicator_key"] == "r_star_lm"
        assert df.iloc[0]["value"] == "1.50"  # 原始 HTML 提取的是字符串，_standardize 中会转为 float
        assert df.iloc[0]["period_date"] == "2023-03-31"

    async def test_skips_footnotes(self, lm_config):
        collector = MacroRichmondHTMLCollector(lm_config)
        df = await collector.parse_raw(HTML_CONTENT)
        # 脚注行应被跳过
        assert len(df) == 2
        values = [r["value"] for _, r in df.iterrows()]
        assert "Notes:" not in values


class TestNoTablePage:
    """错误处理测试."""

    async def test_empty_page(self, lm_config):
        collector = MacroRichmondHTMLCollector(lm_config)
        with pytest.raises(ValueError, match="无表格且无嵌入"):
            await collector.parse_raw(b"<html><body><p>No tables here</p></body></html>")
