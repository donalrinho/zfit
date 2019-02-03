import pytest

import zfit
from zfit import ztf
import numpy as np

from zfit.util.exception import SubclassingError


def test_pdf_simple_subclass():
    class SimpleGauss(zfit.pdf.ZPDF):
        _PARAMS = ['mu', 'sigma']

        def _unnormalized_pdf(self, x):
            mu = self.parameters['mu']
            # mu = self.params['mu']  # TODO
            sigma = self.parameters['sigma']
            # sigma = self.params['sigma']  # TODO
            x = ztf.unstack_x(x)
            return ztf.exp(-ztf.square((x - mu) / sigma))

    gauss1 = SimpleGauss(obs='obs1', mu=3, sigma=5)

    prob = gauss1.pdf(np.random.random(size=(10, 1)), norm_range=(-4, 5))
    zfit.run(prob)

    with pytest.raises(ValueError):
        gauss2 = SimpleGauss('obs1', 1., sigma=5.)
    with pytest.raises(SubclassingError):
        class SimpleGauss2(zfit.pdf.ZPDF):

            def _unnormalized_pdf(self, x):
                mu = self.parameters['mu']
                # mu = self.params['mu']  # TODO
                sigma = self.parameters['sigma']
                # sigma = self.params['sigma']  # TODO
                x = ztf.unstack_x(x)
                return ztf.exp(-ztf.square((x - mu) / sigma))
