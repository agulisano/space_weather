from datetime import datetime
from unittest import mock

import numpy as np

import pandas as pd
from pandas import Timestamp

from solarwindpy.wind import DataManager, MagneticField, Period


FAKE_DATAFRAME = pd.DataFrame(
    {
        "Time": [
            datetime(2021, 1, 1, 0, 0, 0),
            datetime(2021, 1, 1, 0, 30, 0),
            datetime(2021, 1, 1, 1, 0, 0),
        ],
        "BGSE_0": [1.0, -1.0, 0.0],
        "BGSE_1": [2.0, -2.0, 1.0],
        "BGSE_2": [3.0, -3.0, 2.0],
    }
).set_index("Time")

EXPECTED_CDF_RESULT = [
    MagneticField(Timestamp(2021, 1, 1, 0, 0, 0), 1.0, 2.0, 3.0),
    MagneticField(Timestamp(2021, 1, 1, 0, 30, 0), -1.0, -2.0, -3.0),
    MagneticField(Timestamp(2021, 1, 1, 1, 0, 0), 0.0, 1.0, 2.0),
]

FAKE_MAGNETIC_FIELDS = [
    MagneticField(Timestamp(2021, 1, 1, 0, 0, 0), np.inf, 2.0, 3.0),
    MagneticField(Timestamp(2021, 1, 1, 0, 30, 0), np.inf, np.inf, np.inf),
    MagneticField(Timestamp(2021, 1, 1, 0, 30, 0), np.nan, -2.0, -3.0),
    MagneticField(Timestamp(2021, 1, 1, 0, 30, 0), np.nan, np.nan, np.nan),
    MagneticField(Timestamp(2021, 1, 1, 0, 0, 0), 1.0, 2.0, 3.0),
    MagneticField(Timestamp(2021, 1, 1, 0, 30, 0), -1.0, -2.0, -3.0),
    MagneticField(Timestamp(2021, 1, 1, 1, 0, 0), 0.0, 1.0, 2.0),
]


class FakeGenericTimeSeries:
    """
    TODO: Maybe we can replace the Fake class by a Mock object
        with a method called to_dataframe.
    """

    def __init__(self, fake_dataframe):
        self._dataframe = fake_dataframe

    def __call__(self):
        return self._dataframe

    def to_dataframe(self):
        return self._dataframe


def test_get_cdf_data():
    """
    TODO: Add unit tests for the cases of empty Generic Series
        Objects (should we raise an exception?)
    """
    fake_generic_series_object = FakeGenericTimeSeries(FAKE_DATAFRAME)
    with mock.patch(
        "heliopy.data.wind.mfi_h0", return_value=fake_generic_series_object
    ):
        fake_cdf_data = DataManager.get_gse_magnetic_vector(
            Period(
                datetime(2021, 1, 1, 0, 0, 0), datetime(2021, 1, 1, 1, 0, 0)
            )
        )
    assert sorted(fake_cdf_data, key=lambda x: x.time) == sorted(
        EXPECTED_CDF_RESULT, key=lambda x: x.time
    )


def test_filter_nan_and_inf_values():
    assert (
        DataManager.filter_nan_and_inf_values(FAKE_MAGNETIC_FIELDS)
        == EXPECTED_CDF_RESULT
    )
