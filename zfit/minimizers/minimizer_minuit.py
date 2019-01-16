from typing import List, Union

import iminuit
import tensorflow as tf

from ..core.parameter import Parameter
from ..core.minimizer import BaseMinimizer


class MinuitMinimizer(BaseMinimizer):
    _DEFAULT_name = "MinuitMinimizer"

    def __init__(self, *args, **kwargs):
        self._minuit_minimizer = None
        self._error_methods['minos'] = self._minuit_minos  # before super call!
        self._error_methods['default'] = self._error_methods['minos']  # before super call!
        super().__init__(*args, **kwargs)

    def _minimize(self, params: List[Parameter]):
        loss = self.loss.value()
        gradients = tf.gradients(loss, params)
        assign_params = self._extract_assign_method(params=params)

        def func(values):

            # feed_dict = {p: v for p, v in zip(placeholders, value)}
            # self.sess.run(updated_params, feed_dict=feed_dict)
            for param, value in zip(params, values):
                param.load(value=value, session=self.sess)
            # loss_new = tf.identity(loss)
            loss_new = loss
            loss_evaluated = self.sess.run(loss_new)
            # print("Current loss:", loss_evaluated)
            # print("Current value:", value)
            return loss_evaluated

        def grad_func(values):
            # feed_dict = {p: v for p, v in zip(placeholders, value)}
            # self.sess.run(updated_params, feed_dict=feed_dict)
            for param, value in zip(params, values):
                param.load(value=value, session=self.sess)
            # gradients1 = tf.identity(gradients)
            gradients1 = gradients
            gradients_values = self.sess.run(gradients1)
            return gradients_values

        # create Minuit compatible names
        error_limit_kwargs = {}
        param_lower_upper_step = tuple(
            (param, param.lower_limit, param.upper_limit, param.step_size)
            for param in params)
        param_lower_upper_step = self.sess.run(param_lower_upper_step)
        for param, (value, low, up, step) in zip(params, param_lower_upper_step):
            param_kwargs = {}
            param_kwargs[param.name] = value
            param_kwargs['limit_' + param.name] = low, up
            param_kwargs['error_' + param.name] = step

            error_limit_kwargs.update(param_kwargs)
        params_name = [param.name for param in params]

        minimizer = iminuit.Minuit(fcn=func, use_array_call=True,
                                   grad=grad_func,
                                   forced_parameters=params_name,
                                   **error_limit_kwargs)
        self._minuit_minimizer = minimizer
        result = minimizer.migrad(precision=self.tolerance, **self._current_error_options)
        params = [p_dict for p_dict in result[1]]
        self.sess.run([assign(p['value']) for assign, p in zip(assign_params, params)])

        edm = result[0]['edm']
        fmin = result[0]['fval']
        status = result[0]

        self.get_state(copy=False)._set_new_state(params=params, edm=edm, fmin=fmin, status=status)
        return self.get_state(copy=False)  # HACK(mayou36): copy not working?

    def _minuit_minos(self, params=None, sigma=1.0):
        if params is None:
            params = self.get_parameters()
        params_name = self._extract_parameter_names(params=params)
        result = [self._minuit_minimizer.minos(var=p_name) for p_name in params_name][-1]  # returns every var
        result = {p_name: result[p_name] for p_name in params_name}
        for error_dict in result.values():
            error_dict['lower_error'] = error_dict['lower']  # TODO change value for protocol?
            error_dict['upper_error'] = error_dict['upper']  # TODO change value for protocol?
        return result

    def _hesse(self, params=None):
        params_name = self._extract_parameter_names(params=params)
        result = self._minuit_minimizer.hesse()
        result = {p_dict.pop('name'): p_dict for p_dict in result if params is None or p_dict['name'] in params_name}
        return result