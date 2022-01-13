import pytest
from Models import NCCFunctions
from Models.Config import Config

dnorsIP = '100.64.2.249'
config = Config(ncc='OLDBM',dnorsIP=dnorsIP)

@pytest.mark.timeout(120)
def test01_change_ncc0_to_the_new_dnor():
    NCCFunctions.change_NCCC_config(config.ncc0,config)

@pytest.mark.timeout(120)
@pytest.mark.skipif((config.ncc1=='na') or (not config.ncc1), reason=f"need to have ncc1 configured on ncc.proprerties file")
def test02_change_ncc1_to_the_new_dnor():
    NCCFunctions.change_NCCC_config(config.ncc1,config)
