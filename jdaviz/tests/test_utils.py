import pytest
import warnings

from asdf.exceptions import AsdfWarning
from jdaviz import utils


@pytest.mark.parametrize("test_input,expected", [(0, 'a'), (1, 'b'), (25, 'z'), (26, 'aa'),
                                                 (701, 'zz'), (702, '{a')])
def test_alpha_index(test_input, expected):
    assert utils.alpha_index(test_input) == expected


def test_alpha_index_exceptions():
    with pytest.raises(TypeError, match="index must be an integer"):
        utils.alpha_index(4.2)
    with pytest.raises(ValueError, match="index must be positive"):
        utils.alpha_index(-1)


def test_uri_to_download_bad_scheme(imviz_helper):
    uri = "file://path/to/file.fits"
    with pytest.raises(ValueError, match='URI file://path/to/file.fits with scheme file'):
        imviz_helper.load_data(uri)


@pytest.mark.remote_data
def test_uri_to_download_specviz(specviz_helper):
    uri = "mast:JWST/product/jw02732-o004_t004_miri_ch1-shortmediumlong_x1d.fits"
    specviz_helper.load_data(uri, cache=True)


@pytest.mark.remote_data
def test_uri_to_download_specviz2d(specviz2d_helper):
    uri = "mast:JWST/product/jw01324-o006_s00005_nirspec_f100lp-g140h_s2d.fits"
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', AsdfWarning)
        specviz2d_helper.load_data(uri, cache=True)
