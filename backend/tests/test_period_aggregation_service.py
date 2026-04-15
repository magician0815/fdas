"""
Period aggregation service tests.

Tests for weekly/monthly K-line aggregation from daily data.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import calendar

from app.services.period_aggregation_service import (
    PeriodType,
    get_week_bounds,
    get_month_bounds,
    aggregate_to_weekly,
    aggregate_to_monthly,
    PeriodAggregationService,
)


# =====================
# PeriodType Tests
# =====================

class TestPeriodType:
    """PeriodType enum tests."""

    def test_period_type_daily(self):
        """Test DAILY constant value."""
        assert PeriodType.DAILY == "daily"

    def test_period_type_weekly(self):
        """Test WEEKLY constant value."""
        assert PeriodType.WEEKLY == "weekly"

    def test_period_type_monthly(self):
        """Test MONTHLY constant value."""
        assert PeriodType.MONTHLY == "monthly"

    def test_period_type_minute_1(self):
        """Test MINUTE_1 constant value."""
        assert PeriodType.MINUTE_1 == "1"

    def test_period_type_minute_5(self):
        """Test MINUTE_5 constant value."""
        assert PeriodType.MINUTE_5 == "5"

    def test_period_type_minute_15(self):
        """Test MINUTE_15 constant value."""
        assert PeriodType.MINUTE_15 == "15"

    def test_period_type_minute_30(self):
        """Test MINUTE_30 constant value."""
        assert PeriodType.MINUTE_30 == "30"

    def test_period_type_minute_60(self):
        """Test MINUTE_60 constant value."""
        assert PeriodType.MINUTE_60 == "60"


# =====================
# get_week_bounds Tests
# =====================

class TestGetWeekBounds:
    """get_week_bounds helper function tests."""

    def test_week_bounds_monday(self):
        """Test week bounds for Monday (start of week)."""
        # 2026-04-13 is Monday (weekday 0)
        d = date(2026, 4, 13)
        monday, sunday = get_week_bounds(d)
        assert monday == date(2026, 4, 13)
        assert sunday == date(2026, 4, 19)

    def test_week_bounds_tuesday(self):
        """Test week bounds for Tuesday."""
        # 2026-04-14 is Tuesday (weekday 1)
        d = date(2026, 4, 14)
        monday, sunday = get_week_bounds(d)
        assert monday == date(2026, 4, 13)
        assert sunday == date(2026, 4, 19)

    def test_week_bounds_sunday(self):
        """Test week bounds for Sunday (end of week)."""
        # 2026-04-19 is Sunday (weekday 6)
        d = date(2026, 4, 19)
        monday, sunday = get_week_bounds(d)
        assert monday == date(2026, 4, 13)
        assert sunday == date(2026, 4, 19)

    def test_week_bounds_midweek(self):
        """Test week bounds for Wednesday."""
        # 2026-04-15 is Wednesday (weekday 2)
        d = date(2026, 4, 15)
        monday, sunday = get_week_bounds(d)
        assert monday == date(2026, 4, 13)
        assert sunday == date(2026, 4, 19)

    def test_week_bounds_year_boundary(self):
        """Test week bounds across year boundary."""
        # December 31, 2025 is Wednesday
        d = date(2025, 12, 31)
        monday, sunday = get_week_bounds(d)
        assert monday == date(2025, 12, 29)
        assert sunday == date(2026, 1, 4)

    def test_week_bounds_leap_year_february(self):
        """Test week bounds in leap year February."""
        # 2024 is a leap year
        d = date(2024, 2, 29)  # Thursday in leap year
        monday, sunday = get_week_bounds(d)
        assert monday == date(2024, 2, 26)
        assert sunday == date(2024, 3, 3)


# =====================
# get_month_bounds Tests
# =====================

class TestGetMonthBounds:
    """get_month_bounds helper function tests."""

    def test_month_bounds_first_day(self):
        """Test month bounds for first day of month."""
        d = date(2026, 4, 1)
        first_day, last_day = get_month_bounds(d)
        assert first_day == date(2026, 4, 1)
        assert last_day == date(2026, 4, 30)

    def test_month_bounds_last_day(self):
        """Test month bounds for last day of month."""
        d = date(2026, 4, 30)
        first_day, last_day = get_month_bounds(d)
        assert first_day == date(2026, 4, 1)
        assert last_day == date(2026, 4, 30)

    def test_month_bounds_mid_month(self):
        """Test month bounds for middle of month."""
        d = date(2026, 4, 15)
        first_day, last_day = get_month_bounds(d)
        assert first_day == date(2026, 4, 1)
        assert last_day == date(2026, 4, 30)

    def test_month_bounds_31_day_month(self):
        """Test month bounds for 31-day month."""
        d = date(2026, 1, 15)
        first_day, last_day = get_month_bounds(d)
        assert first_day == date(2026, 1, 1)
        assert last_day == date(2026, 1, 31)

    def test_month_bounds_february_non_leap(self):
        """Test month bounds for February in non-leap year."""
        d = date(2026, 2, 15)
        first_day, last_day = get_month_bounds(d)
        assert first_day == date(2026, 2, 1)
        assert last_day == date(2026, 2, 28)

    def test_month_bounds_february_leap_year(self):
        """Test month bounds for February in leap year."""
        d = date(2024, 2, 15)
        first_day, last_day = get_month_bounds(d)
        assert first_day == date(2024, 2, 1)
        assert last_day == date(2024, 2, 29)

    def test_month_bounds_year_boundary(self):
        """Test month bounds for December."""
        d = date(2025, 12, 15)
        first_day, last_day = get_month_bounds(d)
        assert first_day == date(2025, 12, 1)
        assert last_day == date(2025, 12, 31)


# =====================
# aggregate_to_weekly Tests
# =====================

class TestAggregateToWeekly:
    """aggregate_to_weekly function tests."""

    def test_aggregate_empty_data(self):
        """Test aggregation with empty input."""
        result = aggregate_to_weekly([])
        assert result == []

    def test_aggregate_single_day(self):
        """Test aggregation with single day data."""
        daily_data = [
            {"date": "2026-04-13", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1000}
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        assert result[0]["date"] == "2026-04-13"
        assert result[0]["open"] == 7.2
        assert result[0]["close"] == 7.3
        assert result[0]["high"] == 7.35
        assert result[0]["low"] == 7.15
        assert result[0]["volume"] == 1000
        assert result[0]["days"] == 1

    def test_aggregate_full_week(self):
        """Test aggregation with full week (5 trading days)."""
        # Week of April 13-19, 2026 (Mon-Sun)
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},  # Monday
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},  # Tuesday
            {"date": "2026-04-15", "open": 7.2, "close": 7.15, "high": 7.22, "low": 7.1, "volume": 900},   # Wednesday
            {"date": "2026-04-16", "open": 7.15, "close": 7.25, "high": 7.3, "low": 7.1, "volume": 1200},  # Thursday
            {"date": "2026-04-17", "open": 7.25, "close": 7.3, "high": 7.35, "low": 7.2, "volume": 1300},  # Friday
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        weekly = result[0]
        # Open = first day's open
        assert weekly["open"] == 7.0
        # Close = last day's close
        assert weekly["close"] == 7.3
        # High = max of all highs
        assert weekly["high"] == 7.35
        # Low = min of all lows
        assert weekly["low"] == 6.95
        # Volume = sum of all volumes
        assert weekly["volume"] == 5500
        # Days count
        assert weekly["days"] == 5
        # Week bounds
        assert weekly["week_start"] == "2026-04-13"
        assert weekly["week_end"] == "2026-04-19"

    def test_aggregate_partial_week(self):
        """Test aggregation with partial week (3 days)."""
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            {"date": "2026-04-15", "open": 7.2, "close": 7.15, "high": 7.22, "low": 7.1, "volume": 900},
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        assert result[0]["open"] == 7.0
        assert result[0]["close"] == 7.15
        assert result[0]["days"] == 3

    def test_aggregate_multiple_weeks(self):
        """Test aggregation spanning multiple weeks."""
        # Week 1 (Apr 13-17)
        # Week 2 (Apr 20-24, Monday is Apr 20)
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            # Week 2 starts Apr 20 (Monday)
            {"date": "2026-04-20", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1200},
            {"date": "2026-04-21", "open": 7.4, "close": 7.35, "high": 7.42, "low": 7.3, "volume": 800},
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 2
        # Week 1
        assert result[0]["date"] == "2026-04-13"
        assert result[0]["open"] == 7.0
        assert result[0]["close"] == 7.2
        assert result[0]["days"] == 2
        # Week 2
        assert result[1]["date"] == "2026-04-20"
        assert result[1]["open"] == 7.3
        assert result[1]["close"] == 7.35
        assert result[1]["days"] == 2

    def test_aggregate_with_date_objects(self):
        """Test aggregation with date objects instead of strings."""
        daily_data = [
            {"date": date(2026, 4, 13), "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": date(2026, 4, 14), "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        assert result[0]["date"] == "2026-04-13"

    def test_aggregate_with_datetime_objects(self):
        """Test aggregation with datetime objects."""
        daily_data = [
            {"date": datetime(2026, 4, 13, 10, 30), "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": datetime(2026, 4, 14, 11, 0), "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        assert result[0]["date"] == "2026-04-13"

    def test_aggregate_invalid_date_string(self):
        """Test aggregation skips invalid date strings."""
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "invalid-date", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        assert result[0]["days"] == 1

    def test_aggregate_missing_date(self):
        """Test aggregation skips items with missing date."""
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},  # No date
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        assert result[0]["days"] == 1

    def test_aggregate_change_pct_positive(self):
        """Test positive change percentage calculation."""
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.35, "high": 7.4, "low": 7.05, "volume": 1100},  # Close up
        ]
        result = aggregate_to_weekly(daily_data)
        # Open = 7.0, Close = 7.35, Change = (7.35 - 7.0) / 7.0 * 100 = 5%
        assert abs(result[0]["change_pct"] - 5.0) < 0.01

    def test_aggregate_change_pct_negative(self):
        """Test negative change percentage calculation."""
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 6.8, "high": 7.15, "low": 6.75, "volume": 1100},  # Close down
        ]
        result = aggregate_to_weekly(daily_data)
        # Open = 7.0, Close = 6.8, Change = (6.8 - 7.0) / 7.0 * 100 = -2.857%
        assert abs(result[0]["change_pct"] - (-2.8571)) < 0.01

    def test_aggregate_amplitude(self):
        """Test amplitude calculation."""
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.5, "low": 6.5, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = aggregate_to_weekly(daily_data)
        # Open = 7.0, High = 7.5, Low = 6.5, Amplitude = (7.5 - 6.5) / 7.0 * 100 = 14.29%
        assert abs(result[0]["amplitude"] - 14.2857) < 0.01

    def test_aggregate_zero_open(self):
        """Test handling zero open price."""
        daily_data = [
            {"date": "2026-04-13", "open": 0, "close": 7.1, "high": 7.15, "low": 0, "volume": 1000},
        ]
        result = aggregate_to_weekly(daily_data)
        # Zero open should result in zero change_pct and amplitude
        assert result[0]["change_pct"] == 0
        assert result[0]["amplitude"] == 0

    def test_aggregate_missing_fields(self):
        """Test aggregation with missing OHLC fields."""
        daily_data = [
            {"date": "2026-04-13"},  # Missing OHLC fields
        ]
        result = aggregate_to_weekly(daily_data)
        assert len(result) == 1
        # Should use default values (0)
        assert result[0]["open"] == 0
        assert result[0]["close"] == 0
        assert result[0]["high"] == 0
        assert result[0]["low"] == 0
        assert result[0]["volume"] == 0


# =====================
# aggregate_to_monthly Tests
# =====================

class TestAggregateToMonthly:
    """aggregate_to_monthly function tests."""

    def test_aggregate_empty_data(self):
        """Test monthly aggregation with empty input."""
        result = aggregate_to_monthly([])
        assert result == []

    def test_aggregate_single_day(self):
        """Test monthly aggregation with single day."""
        daily_data = [
            {"date": "2026-04-15", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1000}
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 1
        assert result[0]["date"] == "2026-04-01"  # First day of month
        assert result[0]["month_start"] == "2026-04-01"
        assert result[0]["month_end"] == "2026-04-30"

    def test_aggregate_full_month(self):
        """Test aggregation with full month data."""
        # Using sequential dates in April 2026
        daily_data = [
            {"date": "2026-04-01", "open": 7.0, "close": 7.05, "high": 7.1, "low": 6.95, "volume": 1000},
            {"date": "2026-04-02", "open": 7.05, "close": 7.1, "high": 7.15, "low": 7.0, "volume": 1100},
            {"date": "2026-04-03", "open": 7.1, "close": 7.15, "high": 7.2, "low": 7.05, "volume": 900},
            {"date": "2026-04-28", "open": 7.3, "close": 7.35, "high": 7.4, "low": 7.25, "volume": 1200},
            {"date": "2026-04-29", "open": 7.35, "close": 7.4, "high": 7.45, "low": 7.3, "volume": 1300},
            {"date": "2026-04-30", "open": 7.4, "close": 7.45, "high": 7.5, "low": 7.35, "volume": 1400},
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 1
        monthly = result[0]
        # Open = first day's open (sorted by date)
        assert monthly["open"] == 7.0
        # Close = last day's close (sorted by date)
        assert monthly["close"] == 7.45
        # High = max of all highs
        assert monthly["high"] == 7.5
        # Low = min of all lows
        assert monthly["low"] == 6.95
        # Volume = sum
        assert monthly["volume"] == 6900
        # Days count
        assert monthly["days"] == 6

    def test_aggregate_multiple_months(self):
        """Test aggregation spanning multiple months."""
        daily_data = [
            # April
            {"date": "2026-04-01", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-15", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            # May
            {"date": "2026-05-01", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1200},
            {"date": "2026-05-15", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1300},
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 2
        # April
        assert result[0]["date"] == "2026-04-01"
        assert result[0]["open"] == 7.0
        assert result[0]["close"] == 7.2
        assert result[0]["days"] == 2
        # May
        assert result[1]["date"] == "2026-05-01"
        assert result[1]["open"] == 7.2
        assert result[1]["close"] == 7.4
        assert result[1]["days"] == 2

    def test_aggregate_february_leap_year(self):
        """Test aggregation for February in leap year."""
        daily_data = [
            {"date": "2024-02-01", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2024-02-29", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 1
        assert result[0]["month_end"] == "2024-02-29"

    def test_aggregate_february_non_leap(self):
        """Test aggregation for February in non-leap year."""
        daily_data = [
            {"date": "2026-02-01", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-02-28", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 1
        assert result[0]["month_end"] == "2026-02-28"

    def test_aggregate_with_date_objects(self):
        """Test monthly aggregation with date objects."""
        daily_data = [
            {"date": date(2026, 4, 15), "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 1
        assert result[0]["date"] == "2026-04-01"

    def test_aggregate_with_datetime_objects(self):
        """Test monthly aggregation with datetime objects."""
        daily_data = [
            {"date": datetime(2026, 4, 15, 10, 30), "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 1
        assert result[0]["date"] == "2026-04-01"

    def test_aggregate_invalid_date_string(self):
        """Test monthly aggregation skips invalid date strings."""
        daily_data = [
            {"date": "2026-04-15", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "invalid", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = aggregate_to_monthly(daily_data)
        assert len(result) == 1
        assert result[0]["days"] == 1

    def test_aggregate_change_pct_calculation(self):
        """Test monthly change percentage calculation."""
        daily_data = [
            {"date": "2026-04-01", "open": 7.0, "close": 7.05, "high": 7.1, "low": 6.95, "volume": 1000},
            {"date": "2026-04-30", "open": 7.4, "close": 7.7, "high": 7.75, "low": 7.35, "volume": 1100},
        ]
        result = aggregate_to_monthly(daily_data)
        # Open = 7.0, Close = 7.7, Change = (7.7 - 7.0) / 7.0 * 100 = 10%
        assert abs(result[0]["change_pct"] - 10.0) < 0.01

    def test_aggregate_amplitude_calculation(self):
        """Test monthly amplitude calculation."""
        daily_data = [
            {"date": "2026-04-01", "open": 7.0, "close": 7.05, "high": 7.5, "low": 6.5, "volume": 1000},
            {"date": "2026-04-30", "open": 7.4, "close": 7.5, "high": 7.55, "low": 7.35, "volume": 1100},
        ]
        result = aggregate_to_monthly(daily_data)
        # Open = 7.0, High = 7.55, Low = 6.5, Amplitude = (7.55 - 6.5) / 7.0 * 100 = 15%
        assert abs(result[0]["amplitude"] - 15.0) < 0.01

    def test_aggregate_zero_open(self):
        """Test monthly aggregation with zero open."""
        daily_data = [
            {"date": "2026-04-15", "open": 0, "close": 7.1, "high": 7.15, "low": 0, "volume": 1000},
        ]
        result = aggregate_to_monthly(daily_data)
        assert result[0]["change_pct"] == 0
        assert result[0]["amplitude"] == 0


# =====================
# PeriodAggregationService Tests
# =====================

class TestPeriodAggregationService:
    """PeriodAggregationService class tests."""

    def test_service_init(self):
        """Test service initialization."""
        service = PeriodAggregationService()
        assert service is not None

    def test_aggregate_daily_type(self):
        """Test aggregate with DAILY type returns original data."""
        service = PeriodAggregationService()
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000}
        ]
        result = service.aggregate(daily_data, PeriodType.DAILY)
        assert result == daily_data

    def test_aggregate_weekly_type(self):
        """Test aggregate with WEEKLY type."""
        service = PeriodAggregationService()
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = service.aggregate(daily_data, PeriodType.WEEKLY)
        assert len(result) == 1
        assert "week_start" in result[0]

    def test_aggregate_monthly_type(self):
        """Test aggregate with MONTHLY type."""
        service = PeriodAggregationService()
        daily_data = [
            {"date": "2026-04-01", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-15", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
        ]
        result = service.aggregate(daily_data, PeriodType.MONTHLY)
        assert len(result) == 1
        assert "month_start" in result[0]

    def test_aggregate_minute_type(self):
        """Test aggregate with minute type returns original data."""
        service = PeriodAggregationService()
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000}
        ]
        # Minute types return original data (no aggregation)
        result = service.aggregate(daily_data, PeriodType.MINUTE_1)
        assert result == daily_data

        result = service.aggregate(daily_data, PeriodType.MINUTE_5)
        assert result == daily_data

    def test_aggregate_empty_data(self):
        """Test aggregate with empty data."""
        service = PeriodAggregationService()
        result = service.aggregate([], PeriodType.WEEKLY)
        assert result == []

        result = service.aggregate([], PeriodType.MONTHLY)
        assert result == []

    def test_aggregate_with_indicators_basic(self):
        """Test aggregate_with_indicators returns structured result."""
        service = PeriodAggregationService()
        mock_tech_service = MagicMock()
        mock_tech_service.calculate_ma.return_value = [7.1, 7.2]
        mock_tech_service.calculate_macd.return_value = {
            "dif": [0.1],
            "dea": [0.05],
            "macd": [0.05]
        }

        # Use enough data for aggregation
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            {"date": "2026-04-15", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1200},
            {"date": "2026-04-16", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1300},
            {"date": "2026-04-17", "open": 7.4, "close": 7.5, "high": 7.55, "low": 7.35, "volume": 1400},
        ]

        with patch('app.services.technical_service.TechnicalService') as MockTS:
            MockTS.return_value = mock_tech_service
            result = service.aggregate_with_indicators(
                daily_data,
                PeriodType.WEEKLY,
                ma_periods=[5],
                macd_params={"fast": 12, "slow": 26, "signal": 9}
            )
            assert "data" in result
            assert "ma" in result
            assert "macd" in result
            assert "period_type" in result
            assert result["period_type"] == PeriodType.WEEKLY

    def test_aggregate_with_indicators_insufficient_data(self):
        """Test aggregate_with_indicators with insufficient data for MA."""
        service = PeriodAggregationService()
        mock_tech_service = MagicMock()
        mock_tech_service.calculate_macd.return_value = {"dif": [], "dea": [], "macd": []}

        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
        ]

        with patch('app.services.technical_service.TechnicalService') as MockTS:
            MockTS.return_value = mock_tech_service
            result = service.aggregate_with_indicators(
                daily_data,
                PeriodType.WEEKLY,
                ma_periods=[5],  # Need 5 data points but only have 1
                macd_params={"fast": 12, "slow": 26, "signal": 9}
            )
            # Should not have MA data due to insufficient points
            assert result["ma"] == {}

    def test_aggregate_with_indicators_custom_ma_periods(self):
        """Test aggregate_with_indicators with custom MA periods."""
        service = PeriodAggregationService()
        mock_tech_service = MagicMock()
        mock_tech_service.calculate_ma.return_value = [7.15]
        mock_tech_service.calculate_macd.return_value = {"dif": [], "dea": [], "macd": []}

        # Use data spanning multiple weeks to get 3 aggregated points
        # Week 1: Apr 13 (Monday), Week 2: Apr 20 (Monday), Week 3: Apr 27 (Monday)
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-20", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            {"date": "2026-04-27", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1200},
        ]

        with patch('app.services.technical_service.TechnicalService') as MockTS:
            MockTS.return_value = mock_tech_service
            result = service.aggregate_with_indicators(
                daily_data,
                PeriodType.WEEKLY,
                ma_periods=[2, 3],  # Custom periods
                macd_params={"fast": 12, "slow": 26, "signal": 9}
            )
            assert "ma2" in result["ma"]
            assert "ma3" in result["ma"]

    def test_aggregate_with_indicators_custom_macd_params(self):
        """Test aggregate_with_indicators with custom MACD params."""
        service = PeriodAggregationService()
        mock_tech_service = MagicMock()
        mock_tech_service.calculate_ma.return_value = [7.1]
        mock_tech_service.calculate_macd.return_value = {"dif": [0.1], "dea": [0.05], "macd": [0.05]}

        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            {"date": "2026-04-15", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1200},
            {"date": "2026-04-16", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1300},
            {"date": "2026-04-17", "open": 7.4, "close": 7.5, "high": 7.55, "low": 7.35, "volume": 1400},
        ]

        with patch('app.services.technical_service.TechnicalService') as MockTS:
            MockTS.return_value = mock_tech_service
            result = service.aggregate_with_indicators(
                daily_data,
                PeriodType.WEEKLY,
                ma_periods=[5],
                macd_params={"fast": 5, "slow": 10, "signal": 3}  # Custom params
            )
            assert "macd" in result

    def test_aggregate_with_indicators_default_params(self):
        """Test aggregate_with_indicators with default params."""
        service = PeriodAggregationService()
        mock_tech_service = MagicMock()
        mock_tech_service.calculate_ma.return_value = [7.1]
        mock_tech_service.calculate_macd.return_value = {"dif": [], "dea": [], "macd": []}

        # Use enough data points
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            {"date": "2026-04-15", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1200},
            {"date": "2026-04-16", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1300},
            {"date": "2026-04-17", "open": 7.4, "close": 7.5, "high": 7.55, "low": 7.35, "volume": 1400},
        ]

        with patch('app.services.technical_service.TechnicalService') as MockTS:
            MockTS.return_value = mock_tech_service
            # Call without specifying ma_periods and macd_params (uses defaults)
            result = service.aggregate_with_indicators(
                daily_data,
                PeriodType.WEEKLY
            )
            assert "ma" in result
            assert "macd" in result


class TestPeriodAggregationServiceWithMock:
    """PeriodAggregationService tests with mocked TechnicalService."""

    def test_aggregate_with_indicators_mock_technical(self):
        """Test aggregate_with_indicators with mocked TechnicalService."""
        service = PeriodAggregationService()

        mock_tech_service = MagicMock()
        mock_tech_service.calculate_ma.return_value = [7.1, 7.2, 7.3]
        mock_tech_service.calculate_macd.return_value = {
            "dif": [0.1, 0.2],
            "dea": [0.05, 0.1],
            "macd": [0.05, 0.1]
        }

        # Use data spanning multiple weeks to get 5 weekly points
        # Week 1: Apr 13, Week 2: Apr 20, Week 3: Apr 27, Week 4: May 4, Week 5: May 11
        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-20", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            {"date": "2026-04-27", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1200},
            {"date": "2026-05-04", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1300},
            {"date": "2026-05-11", "open": 7.4, "close": 7.5, "high": 7.55, "low": 7.35, "volume": 1400},
        ]

        # TechnicalService is imported inside the function, patch at module level
        with patch('app.services.technical_service.TechnicalService') as MockTechnicalService:
            MockTechnicalService.return_value = mock_tech_service

            result = service.aggregate_with_indicators(
                daily_data,
                PeriodType.WEEKLY,
                ma_periods=[5]
            )

            # Verify TechnicalService was created
            MockTechnicalService.assert_called_once()

            # Verify calculate_ma was called
            mock_tech_service.calculate_ma.assert_called()

            # Verify structure
            assert "ma" in result
            assert "macd" in result

    def test_aggregate_with_indicators_daily_type(self):
        """Test aggregate_with_indicators with DAILY type."""
        service = PeriodAggregationService()
        mock_tech_service = MagicMock()
        mock_tech_service.calculate_ma.return_value = [7.1]
        mock_tech_service.calculate_macd.return_value = {"dif": [], "dea": [], "macd": []}

        daily_data = [
            {"date": "2026-04-13", "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-14", "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 1100},
            {"date": "2026-04-15", "open": 7.2, "close": 7.3, "high": 7.35, "low": 7.15, "volume": 1200},
            {"date": "2026-04-16", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1300},
            {"date": "2026-04-17", "open": 7.4, "close": 7.5, "high": 7.55, "low": 7.35, "volume": 1400},
        ]

        with patch('app.services.technical_service.TechnicalService') as MockTS:
            MockTS.return_value = mock_tech_service
            result = service.aggregate_with_indicators(
                daily_data,
                PeriodType.DAILY
            )

            # DAILY type should return original data
            assert result["data"] == daily_data
            assert result["period_type"] == PeriodType.DAILY


# =====================
# Coverage Tests (Missing Lines)
# =====================

class TestCoverageMissingLines:
    """Tests to cover missing lines 186 and similar."""

    def test_aggregate_monthly_with_none_date(self):
        """Test monthly aggregation with None date value (covers line 186)."""
        daily_data = [
            {"date": None, "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-15", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1100},
        ]
        result = aggregate_to_monthly(daily_data)
        # None date should be skipped, only valid date processed
        assert len(result) == 1
        assert result[0]["days"] == 1

    def test_aggregate_weekly_with_none_date(self):
        """Test weekly aggregation with None date value."""
        daily_data = [
            {"date": None, "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": "2026-04-15", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1100},
        ]
        result = aggregate_to_weekly(daily_data)
        # None date should be skipped
        assert len(result) == 1

    def test_aggregate_monthly_with_zero_date(self):
        """Test monthly aggregation with zero/False as date (covers line 186)."""
        daily_data = [
            {"date": 0, "open": 7.0, "close": 7.1, "high": 7.15, "low": 6.95, "volume": 1000},
            {"date": False, "open": 7.1, "close": 7.2, "high": 7.25, "low": 7.05, "volume": 900},
            {"date": "2026-04-15", "open": 7.3, "close": 7.4, "high": 7.45, "low": 7.25, "volume": 1100},
        ]
        result = aggregate_to_monthly(daily_data)
        # Zero and False dates should be skipped
        assert len(result) == 1