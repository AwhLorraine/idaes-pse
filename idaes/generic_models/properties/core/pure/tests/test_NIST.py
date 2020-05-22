##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2019, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
Tests for methods from NIST

All methods and parameters from:

https://webbook.nist.gov, retrieved 26 November 2019

All parameter indicies based on conventions used by the source

Authors: Andrew Lee
"""

import pytest

from pyomo.environ import ConcreteModel, Block, value, Var
from pyomo.common.config import ConfigBlock

from idaes.generic_models.properties.core.pure.NIST import *
from idaes.core.util.misc import add_object_reference


@pytest.fixture()
def frame():
    m = ConcreteModel()

    # Create a dummy parameter block
    m.params = Block()

    m.params.config = ConfigBlock(implicit=True)
    m.params.config.parameter_data = {
        "cp_mol_ig_comp_coeff": {'A': 30.09200,
                                 'B': 6.832514,
                                 'C': 6.793435,
                                 'D': -2.534480,
                                 'E': 0.082139,
                                 'F': -250.8810,
                                 'G': 223.3967,
                                 'H': -241.8264},
        "pressure_sat_comp_coeff": {'A': 8.55959,  # +5 for unit conversion
                                    'B': 643.748,
                                    'C': -198.043}}

    # Add necessary parameters to parameter block
    m.params.temperature_ref = Var(initialize=298.15)
    m.params.pressure_ref = Var(initialize=1e5)

    # Create a dummy state block
    m.props = Block([1])
    add_object_reference(m.props[1], "params", m.params)

    m.props[1].temperature = Var(initialize=500)
    m.props[1].pressure = Var(initialize=101325)

    return m


def test_cp_mol_ig_comp(frame):
    cp_mol_ig_comp.build_parameters(frame.params)

    expr = cp_mol_ig_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature)
    assert value(expr) == pytest.approx(35.22, abs=1e-2)

    frame.props[1].temperature.value = 600
    assert value(expr) == pytest.approx(36.32, abs=1e-2)


def test_enth_mol_ig_comp(frame):
    enth_mol_ig_comp.build_parameters(frame.params)

    expr = enth_mol_ig_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature)
    assert value(expr) == pytest.approx(-2130.5, rel=1e-3)

    frame.props[1].temperature.value = 600
    assert value(expr) == pytest.approx(1445, rel=1e-3)


def test_entr_mol_ig_comp(frame):
    entr_mol_ig_comp.build_parameters(frame.params)

    expr = entr_mol_ig_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature)
    assert value(expr) == pytest.approx(206.5, rel=1e-3)

    frame.props[1].temperature.value = 600
    assert value(expr) == pytest.approx(213.1, rel=1e-3)


def test_pressure_sat_comp(frame):
    pressure_sat_comp.build_parameters(frame.params)

    expr = pressure_sat_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature)
    assert value(expr) == pytest.approx(2677137, rel=1e-4)

    frame.props[1].temperature.value = 379
    assert value(expr) == pytest.approx(100490, rel=1e-4)


def test_pressure_sat_comp_dT(frame):
    pressure_sat_comp.build_parameters(frame.params)

    expr = pressure_sat_comp.dT_expression(
        frame.props[1], frame.params, frame.props[1].temperature)

    delta = 1e-4
    val = pressure_sat_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature)
    val_p = pressure_sat_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature+delta)

    dPdT = value((val-val_p)/-delta)

    assert value(expr) == pytest.approx(dPdT, 1e-4)

    frame.props[1].temperature.value = 373.15

    val = pressure_sat_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature)
    val_p = pressure_sat_comp.return_expression(
        frame.props[1], frame.params, frame.props[1].temperature+delta)

    dPdT = value((val-val_p)/-delta)

    assert value(expr) == pytest.approx(dPdT, 1e-4)
