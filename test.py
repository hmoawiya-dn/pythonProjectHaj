import pytest

from Models.Config import Config
from Models.TestConfig import TestConfig

haj='moawiya'
#config = Config(dnor='dn0607')

@pytest.mark.dependency()
def test_1():
    assert (1==1)


@pytest.mark.dependency(depends=['test_1'])
@pytest.mark.skipif((haj=='moawiya'),reason='not here')
def test_2():
    assert (1==0)

@pytest.mark.dependency(depends=['test_2'],reason= 'Hello')
def test_3():
    assert 1==1
