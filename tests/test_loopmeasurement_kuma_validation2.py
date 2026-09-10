import pytest
from KUMA import KUMA


@pytest.fixture
def kuma():
    return KUMA()


def test_getDose_monotonic_with_flux(kuma):
    d1 = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e11,
        wavelength=1.0,
        exp_time=0.02,
    )
    d2 = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=2.0e11,
        wavelength=1.0,
        exp_time=0.02,
    )

    assert d2 > d1
    assert pytest.approx(d2 / d1, rel=1e-6) == 2.0


def test_getDose_monotonic_with_beam_area(kuma):
    d_small = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e12,
        wavelength=1.0,
        exp_time=0.02,
    )
    d_large = kuma.getDose(
        beam_h=10.0,
        beam_v=10.0,
        flux=1.0e12,
        wavelength=1.0,
        exp_time=0.02,
    )

    assert d_large < d_small
    assert pytest.approx(d_small / d_large, rel=1e-6) == 4.0


def test_getDose_monotonic_with_exptime(kuma):
    d1 = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e12,
        wavelength=1.0,
        exp_time=0.01,
    )
    d2 = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e12,
        wavelength=1.0,
        exp_time=0.02,
    )

    assert d2 > d1
    assert pytest.approx(d2 / d1, rel=1e-6) == 2.0


def test_convDoseToExptimeLimit_roundtrip(kuma):
    target_dose = 5.0
    wavelength = 1.0

    exptime = kuma.convDoseToExptimeLimit(
        dose=target_dose,
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e12,
        wavelength=wavelength,
    )

    dose_back = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e12,
        wavelength=wavelength,
        exp_time=exptime,
    )

    assert pytest.approx(dose_back, rel=1e-3) == target_dose


def test_getDose_depends_on_wavelength(kuma):
    """
    wavelength API になっていることの確認。
    同じ flux / beam / exp_time なら wavelength が変われば dose も変わる。
    """
    d1 = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e12,
        wavelength=1.0,
        exp_time=0.02,
    )
    d2 = kuma.getDose(
        beam_h=5.0,
        beam_v=5.0,
        flux=1.0e12,
        wavelength=1.2,
        exp_time=0.02,
    )

    assert d1 != d2


def test_getDose_rejects_non_positive_values(kuma):
    with pytest.raises(ValueError):
        kuma.getDose(
            beam_h=0.0,
            beam_v=5.0,
            flux=1.0e12,
            wavelength=1.0,
            exp_time=0.02,
        )

    with pytest.raises(ValueError):
        kuma.getDose(
            beam_h=5.0,
            beam_v=5.0,
            flux=0.0,
            wavelength=1.0,
            exp_time=0.02,
        )

    with pytest.raises(ValueError):
        kuma.getDose(
            beam_h=5.0,
            beam_v=5.0,
            flux=1.0e12,
            wavelength=0.0,
            exp_time=0.02,
        )

    with pytest.raises(ValueError):
        kuma.getDose(
            beam_h=5.0,
            beam_v=5.0,
            flux=1.0e12,
            wavelength=1.0,
            exp_time=0.0,
        )