import logging as _logging

from pytrnsys_process import utils
from pytrnsys_process.deck import extractor
from tests.pytrnsys_process import constants


def test_extract_constants_and_ignore_outputs():
    deck_as_string = """\
CONSTANTS 2
mfrSolverAbsTol = 1e-6
mfrSolverRelTol = 1e-9
CONSTANTS 1
START=7300.0 
EQUATIONS 4
xFracValSrcSugg = [10,1]
THxNetInTrErr = [10,2]
xFracValSrcCtrStat = [10,3]
THxNetInUnsat = [10,4]
TS_GColdConv = [99,7]*-1*1/3600 """
    expected_dict = {
        "mfrSolverAbsTol": 1e-06,
        "mfrSolverRelTol": 1e-09,
        "START": 7300.0,
    }

    extract_equations_and_compare(deck_as_string, expected_dict)


def test_extract_direct_referenced_constants():
    deck_as_string = """\
CONSTANTS 2
dtSim=1/60*2
dtSim_SI = dtSim*3600
EQUATIONS 2
THxNetInMin=2.0
THxNetInOn = THxNetInMin + 0.5"""
    expected_dict = {
        "dtSim": 0.03333333333333333,
        "dtSim_SI": 120.0,
        "THxNetInMin": 2.0,
        "THxNetInOn": 2.5,
    }

    extract_equations_and_compare(deck_as_string, expected_dict)


def test_extract_indirect_referenced_constants():
    deck_as_string = """\
    CONSTANTS 2
    dtSim=1/60*2
    dtSim_SI = dtSim*3600
    EQUATIONS 3
    THxNetInMin=2.0
    THxNetInOn = THxNetInMin + 0.5
    otherConstant =THxNetInOn * dtSim_SI"""
    expected_dict = {
        "THxNetInMin": 2.0,
        "THxNetInOn": 2.5,
        "dtSim": 0.03333333333333333,
        "dtSim_SI": 120.0,
        "otherConstant": 300.0,
    }

    extract_equations_and_compare(deck_as_string, expected_dict)


def test_extract_with_mathematical_functions():
    deck_as_string = """\
CONSTANTS 2
TS_A_Len = 135.0
TS_A_NrSlAx = INT(TS_A_Len*dpNrSlAxRef/dpLengthRef) + 1
CONSTANTS 1
dpNrSlAxRef=10.0
CONSTANTS 1
dpLengthRef = 579.404"""
    expected_dict = {
        "TS_A_Len": 135.0,
        "TS_A_NrSlAx": 3.0,
        "dpLengthRef": 579.404,
        "dpNrSlAxRef": 10.0,
    }

    extract_equations_and_compare(deck_as_string, expected_dict)


def test_extract_const_with_all_supported_mathematical_functions():
    deck_as_string = """\
    CONSTANTS 23
    ae = AE(4,2,1)
    abs = ABS(4.5)
    and = AND(1,0)
    asin = ASIN(1)
    atan = ATAN(4.2)
    cos = COS(8.8)
    eql = EQL(4.2, 4.2)
    exp = EXP(9)
    ge = GE(2,2)
    gt = GT(2,1)
    int = INT(4.269)
    le = LE(1, 1)
    ln = LN(4.6)
    log = LOG(4.9)
    lt = LT(1,2)
    or = OR(1,0)
    max = MAX(69,420)
    min = MIN(69,420)
    mod = MOD(420, 69)
    not = NOT(1)
    sin = SIN(4.9)
    tan = TAN(4.9)
    acos = ACOS(0.5)
    """
    expected_dict = {
        "abs": 4.5,
        'acos': 1.0471975511965979,
        "ae": 0,
        "and": 0,
        "asin": 1.5707963267948966,
        "atan": 1.3370531459259951,
        "cos": -0.811093014061656,
        "eql": 1,
        "exp": 8103.083927575384,
        "ge": 1,
        "gt": 1,
        "int": 4,
        "le": 1,
        "ln": 1.5260563034950492,
        "log": 0.6901960800285137,
        "lt": 1,
        "max": 420,
        "min": 69,
        "mod": 6.0,
        "not": 0,
        "or": 1,
        "sin": -0.9824526126243325,
        "tan": -5.267493065826737,
    }

    extract_equations_and_compare(deck_as_string, expected_dict)


def test_extract_equation_with_value_zero():
    """Make sure maybe_evaluated_value = 0 is not asserted as false"""
    deck_as_string = """\
    CONSTANTS 1
    ratioDHWtoSH_allSinks=0.0"""
    expected_dict = {"ratioDHWtoSH_allSinks": 0.0}

    extract_equations_and_compare(deck_as_string, expected_dict)


def test_extract_double_division_constants():
    deck_as_string = """\
    CONSTANTS 1
    powerScalingFactor=0.6 ! value changed from original by executeTrnsys.py
    CONSTANTS 9
    VIceSscaled=5.0
    BaseDemandGwh=12.4237719
    DemandRefGWh=7.0
    QIceS_MWh =  VIceSscaled*(powerScalingFactor*BaseDemandGwh-DemandRefGWh)
    QIceSrel_kWh_per_m3 = 87.96
    VIceS = QIceS_MWh*1000/QIceSrel_kWh_per_m3
    Tankheight = 2.5
    Tankwidth = (VIceS/Tankheight)^(0.5)
    TankLength = ViceS/Tankheight/TankWidth
"""
    expected_dict = {
        "BaseDemandGwh": 12.4237719,
        "DemandRefGWh": 7,
        "QIceS_MWh": 2.2713157000000006,
        "QIceSrel_kWh_per_m3": 87.96,
        "TankLength": 3.2138539493607574,
        "Tankheight": 2.5,
        "Tankwidth": 3.213853949360758,
        "VIceS": 25.82214301955435,
        "VIceSscaled": 5,
        "powerScalingFactor": 0.6,
    }

    extract_equations_and_compare(deck_as_string, expected_dict)


def test_unsupported_func_call(caplog):
    deck_as_string = """\
CONSTANTS 1
THxNetInSetMaxErr = -0.5
EQUATIONS 1
THxNetInSetMaxErrCheck = GTWARN(THxNetInSetMaxErr, 0, 2)
"""
    with caplog.at_level(_logging.WARNING):
        extractor.parse_deck_for_constant_expressions(deck_as_string)
    assert (
            "On line 4, GTWARN is not supported in THxNetInSetMaxErrCheck=GTWARN(THxNetInSetMaxErr, 0, 2)"
            in caplog.text
    )


def test_handling_of_visit_error_error(caplog):
    deck_as_string = """\
        CONSTANTS 1
        powerScalingFactor=max(3)
"""
    with caplog.at_level(_logging.WARNING):
        extractor.parse_deck_for_constant_expressions(deck_as_string)
    assert (
            "On line 2, unable to compute equation powerScalingFactor=max(3)"
            ' because: Error trying to process rule "func_call"' in caplog.text
    )


def extract_equations_and_compare(deck_as_string, expected_dict):
    result_dict = extractor.parse_deck_for_constant_expressions(deck_as_string)

    assert result_dict == expected_dict


# -------------------------------------------
# Benchmarks
# -------------------------------------------


def test_benchmark_to_extract_ice_storage_deck(benchmark):
    def to_benchmark():
        file_content = utils.get_file_content_as_string(
            constants.DATA_FOLDER / "deck" / "large_icegrids_example.dck"
        )

        extractor.parse_deck_for_constant_expressions(file_content)

    benchmark(to_benchmark)


def test_benchmark_to_extract_solar_prop_ice_slurry_mfs_deck(benchmark):
    def to_benchmark():
        file_content = utils.get_file_content_as_string(
            constants.DATA_FOLDER / "deck" / "SolarPropIceSlurry_mfs.dck"
        )

        extractor.parse_deck_for_constant_expressions(file_content)

    benchmark(to_benchmark)
