import pytest
from file_watcher import FileWatcher, FileCopyJob
from rich.align import Align
from rich.live import Live

@pytest.fixture
def file_watcher():
    app = FileWatcher(parameters_path='tests/data/test_parameters.json')
    return app

    
def test_startup(file_watcher):
    assert file_watcher.parameters_json['voyage'] == 'tester'

def test_timer_countdown(file_watcher):
    file_watcher.timer_countdown()
    assert file_watcher.timers[0]['time'] == 10

def test_table_print(file_watcher):
    table = file_watcher.print_timers_table()
    assert type(table) == Align

def test_set_live_output_and_job_finish(file_watcher):
    with Live() as live:
        file_watcher.set_live_output(live)
        assert type(file_watcher.live_output) == Live
        """
        Include the on job finish because it needs ref to the live console.
        """
        file_watcher.active_job_ids = [1, 2]
        file_watcher.on_job_finish(1)
        assert file_watcher.active_job_ids == [2]

def 