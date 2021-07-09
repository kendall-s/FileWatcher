from os import name
from types import resolve_bases
from util import *

"""
Test the string formatting for the voyage wildcard insertion
"""
def test_fmt_str_with_voyage_typical():
    fmt_str = fmt_str_with_voyage_name('?voyagetesting', 'in2021_v04')
    assert fmt_str == 'in2021_v04testing'

def test_fmt_str_with_voyage_spaces():
    fmt_str = fmt_str_with_voyage_name('hi ?voyage test', 'in2021_v04')
    assert fmt_str == 'hi in2021_v04 test'

"""
Test the read in of parameters 
"""
def test_read_in_parameters():
    params = read_in_parameters('tests/data/test_parameters.json')
    assert list(params.keys()) == ['voyage', 'watching']

"""
Test the checking of files given conditions
"""
def test_check_for_files():
    path = 'tests/data/find_files'
    name_contains = 'racecar'
    file_type = '.csv'
    returned_files = check_for_files(path, name_contains, file_type)
    assert returned_files == ['racecar.csv']

"""
Test the copying of a file from one path to another assuming permissions are O.K
"""
def test_copy_file_succeed(tmpdir):
    # Create file one 
    f = tmpdir.mkdir('source_dir').join('first_file.txt')
    f.write('test')
    tmpdir.mkdir('dest_dir')
    result = copy_file(tmpdir.join('source_dir').join('first_file.txt'), tmpdir.join('dest_dir').join('first_file.txt'))
    
    assert result['outcome'] == 'success'

def test_copy_file_error(tmpdir):
    pass

"""
Checksum creation testing
"""
def test_make_checksum(tmpdir):
    f = tmpdir.mkdir('dir').join('file.txt')
    f.write('1010101010')

    result = make_checksum(tmpdir.join('dir').join('file.txt'))
    assert result == '3fd5c2a0df1ce9dc01f0698adc57c72b'

"""
Checksum verification testing
"""
def test_verify_checksum():
    result = verify_checksums('asdfg', 'asdfg')
    assert result == True


"""
Test WNET connections
"""
def test_create_wnet_connection_succeed():
    """
    Test making a connection that SHOULD succeed
    """
    result = create_wnet_connection('C:/', '', '', '')
    assert result['outcome'] == 'success' 

def test_cancel_wnet_connection_succeed():
    """
    Test that cancelling a connection (fix me)
    """
    result = remove_wnet_connection('')
    assert result['outcome'] == 'error'

