# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
from astropy.tests.helper import assert_quantity_allclose
from ...utils.testing import requires_data, requires_dependency
from ...datasets import gammapy_extra
from ...spectrum import SpectrumObservationList
from ...spectrum.spectrum_fit import SpectrumFit
from ...spectrum.spectrum_grouping import SpectrumGrouping


@requires_dependency('sherpa')
@requires_data('gammapy-extra')
def test_define_groups_and_stack(tmpdir):
    phadir = gammapy_extra.filename('datasets/hess-crab4_pha')
    observations = SpectrumObservationList.read_ogip(phadir)
    observations.write_ogip_data(outdir='ogip_data')
    obs_table = observations.to_observation_table()

    fit = SpectrumFit.from_observation_table(obs_table)
    fit.model = 'PL'
    fit.energy_threshold_low = '1 TeV'
    fit.energy_threshold_high = '10 TeV'
    fit.run(method='sherpa')

    # Test that if we have 4 bands for the 4 runs it gives exactly the same result that before
    # actually 2 runs fall in one band
    # Todo: make displaying groups easier
    # Todo: make meaningful comparison


    group = SpectrumGrouping(observations)
    obs_list = group.define_groups_and_stack(offset_range=[0, 2.5],
                                             n_off_bin=10,
                                             eff_range=[0, 100], n_eff_bin=5,
                                             zen_range=[0., 70.], n_zen_bin=7)

    obs_list.write_ogip_data(outdir='ogip_data_grouped')
    band_obs = obs_list.to_observation_table()

    fit_band2 = SpectrumFit.from_observation_table(band_obs)
    fit_band2.model = 'PL'
    fit_band2.energy_threshold_low = '1 TeV'
    fit_band2.energy_threshold_high = '10 TeV'
    fit_band2.run(method='sherpa')

    assert_quantity_allclose(fit.result.parameters["index"],
                             fit_band2.result.parameters["index"], rtol=1e-1)
    assert_quantity_allclose(fit.result.parameters["norm"],
                             fit_band2.result.parameters["norm"], rtol=1e-1)

    # Test that if we stack all the runs in one band we get a result close than before
    obs_list2 = group.define_groups_and_stack(offset_range=[0, 2.5],
                                              n_off_bin=1, eff_range=[0, 100],
                                              n_eff_bin=1,
                                              zen_range=[0., 70.], n_zen_bin=1)

    obs_list2.write_ogip_data(outdir='ogip_data_grouped_all')
    band_obs2 = obs_list2.to_observation_table()
    fit_band3 = SpectrumFit.from_observation_table(band_obs2)
    fit_band3.model = 'PL'
    fit_band3.energy_threshold_low = '100 GeV'
    fit_band3.energy_threshold_high = '10 TeV'
    fit_band3.run(method='sherpa')

    # Todo: Check why difference is so large
    assert_quantity_allclose(fit.result.parameters["index"],
                             fit_band3.result.parameters["index"], rtol=1e0)
    assert_quantity_allclose(fit_band3.result.parameters["norm"],
                             fit.result.parameters["norm"], rtol=1e0)


@requires_data('gammapy-extra')
def test_define_spectral_groups():
    phadir = gammapy_extra.filename('datasets/hess-crab4_pha')
    observations = SpectrumObservationList.read_ogip(phadir)
    group = SpectrumGrouping(observations)
    obs_groups2 = group.define_spectral_groups(offset_range=[0, 2.5],
                                               n_off_bin=2, eff_range=[0, 100],
                                               n_eff_bin=1, zen_range=[0., 70.],
                                               n_zen_bin=2)
    assert obs_groups2.n_groups == 4