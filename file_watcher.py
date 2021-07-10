import os
from util import *
# Use the time it default timer as it is very spot on and accounts for CPU time
from timeit import default_timer as accurate_timer

from threading import Thread
import time
from time import localtime, strftime

from rich.table import Table
from rich.align import Align
from rich.console import Console
from rich.live import Live

class FileWatcher():

    """
    Flow of operations
    - Start timers based on the jobs listed in the parameters path, assign frequency as the length
    - Count down timers every 1 second
    - Check if a timer count has reached 0
    - Start job thread based on which job has reached 0
    - Add job thread to list of threads, close when completed
    
    """

    def __init__(self, parameters_path=None):
        
        if parameters_path:
            self.parameters_path = parameters_path
        else:
            self.parameters_path = 'parameters.json'

        self.running = True
        self.live_output = None
        self.rich_console = Console()

        self.printing_time = 0

        
        self.parameters_json = read_in_parameters(parameters_path)

        self.start_time = accurate_timer()
        self.end_time = 0

        self.timers = []
        self.job_threads = []
        self.active_job_ids = []   
        self.last_active = {}
        self.files_copied = {}

        self.start_up()

    def set_live_output(self, live_ouput):
        self.live_output = live_ouput

    def start_up(self):
        # Iterate through the parameters file and create timers list
        # In the same step, we will populate the voyage wildcard in the paths
        for i, job in enumerate(self.parameters_json['watching']):
            self.timers.append({'id': job['id'], 'time': int(job['frequency'])})
            self.last_active[job['id']] = 'Not been active yet...'
            self.files_copied[job['id']] = 0

            source_fmt = fmt_str_with_voyage_name(job['source'], self.parameters_json['voyage'])
            dest_fmt = fmt_str_with_voyage_name(job['dest'], self.parameters_json['voyage'])
            name_cont_fmt = fmt_str_with_voyage_name(job['name_contains'], self.parameters_json['voyage'])

            self.parameters_json['watching'][i]['source'] = source_fmt
            self.parameters_json['watching'][i]['dest'] = dest_fmt
            self.parameters_json['watching'][i]['name_contains'] = name_cont_fmt
        
    def print_timers_table(self):
        """
        Create a rich library table for pretty printing the ongoing jobs 
        """
        
        table = Table(
            "Job ID", "From", "To", "Time Remaining", "State", "Last Active", "Files Copied",
            show_header=True, header_style="bold orange1", title="Jobs Ongoing"
        )
        table_centered = Align.center(table)

        for timer in self.timers:
            if timer['id'] in self.active_job_ids:
                active_state = 'Active'
            else:
                active_state = 'Waiting'
            table.add_row(f"{timer['id']}",
                            f"{self.parameters_json['watching'][timer['id']-1]['source']}",
                            f"{self.parameters_json['watching'][timer['id']-1]['dest']}",  
                            f"{timer['time']}", 
                            f'{active_state}', 
                            f"{self.last_active[timer['id']]}",
                            f"{self.files_copied[timer['id']]}")

        return table_centered

    def timer_countdown(self):
        """
        Main countdown loop of the file master class, this is what decrements all the timer
        counts. Upon reaching zero it will spin up a new job thread.
        """
        self.end_time = accurate_timer()
        time_diff = int(self.end_time - self.start_time)

        for i, job_timer in enumerate(self.timers):

            job_id = job_timer['id']
            job_time_remaining = job_timer['time']
            
            if job_id not in self.active_job_ids:
                job_timer['time'] = job_time_remaining - time_diff

            if job_timer['time'] < 0 and job_id not in self.active_job_ids:
                file_params_obj = self.parameters_json['watching'][job_id-1]
                
                # Create the new job and add it to the active jobs list
                self.active_job_ids.append(job_id)
                self.timers[i]['time'] = int(self.parameters_json['watching'][i]['frequency'])
                new_job = FileCopyJob(self, file_params_obj, self.live_output)                
                self.job_threads.append(new_job)

                new_job.start()

        self.start_time = accurate_timer()

    def on_job_finish(self, job_id, num_files_copied):
        self.live_output.console.print(f'Removing job {job_id} from the active list \n')
        self.active_job_ids.remove(job_id)
        self.files_copied[job_id] = num_files_copied
        self.last_active[job_id] = strftime("%Y-%m-%d %H:%M:%S", localtime())

class FileCopyJob(Thread):

    """
    This class handles the copying and checking of a file once it has been actioned as a job
    """

    def __init__(self, parent: FileWatcher, params_obj: dict, live_output: Console):
        Thread.__init__(self)

        self.files_copied = 0
        self.parent = parent
        
        self.live_output = live_output

        """
        Destructure the job info object, not really necessary but for sake of future readability?
        """
        self.id = params_obj['id']

        self.source_host = params_obj['source_host']
        self.source = params_obj['source']

        self.dest_host = params_obj['dest_host']
        self.dest = params_obj['dest']

        self.file_type = params_obj['file_type']
        self.name_contains = params_obj['name_contains']
        
        self.source_domain = params_obj['source_auth']['domain']
        self.source_username = params_obj['source_auth']['username']
        self.source_password = params_obj['source_auth']['password']

        self.dest_domain = params_obj['dest_auth']['domain']
        self.dest_username = params_obj['dest_auth']['username']
        self.dest_password = params_obj['dest_auth']['password']

        self.source_folder_path = self.source_host + '\\' + self.source
        self.dest_folder_path = self.dest_host + '\\' + self.dest

        #self.live_output.console.rule(f'Job ID: {self.id} | {self.source} -> {self.dest}')
        #self.live_output.console.log(f'\nJob thread for ID: {self.id} has been created. Assessing files from {self.source} for copying to {self.dest}')

    def run(self):
        """
        This function is called by the thread start
        """
        source_connection = self.generate_connection(self.source_host, self.source_domain, self.source_username, self.source_password)
        dest_connection = self.generate_connection(self.dest_host, self.dest_domain, self.dest_username, self.dest_password)

        # Ensure both connections are successful before proceeding
        if source_connection['outcome'] == 'success' and dest_connection['outcome'] == 'success':
            
            # Get the source and destination files that match the criteria
            matching_source_files = check_for_files(self.source_folder_path, self.name_contains, self.file_type)
            matching_dest_files = check_for_files(self.dest_folder_path, self.name_contains, self.file_type)

            """
            Changing the logic for checking for new files. First attempt was focused on speed, but the correct approach 
            would be to take your time and check every file, looking at mod times to see if a file has been updated.
            Make sure though, that the source modified time is still less than the latest copy of the processing pc.
            """
            # Lets get the files which are in the source directory but not in the destination directory
            # This type of comparator is asymmetric
            files_to_copy = list(set(matching_source_files) - set(matching_dest_files))
            
            # Now lets check the files which exist in both directories and make sure the modified times are the same
            matching_files = set(matching_source_files) & set(matching_dest_files)
            for file in matching_files:
                source_mod_time = os.path.getmtime(self.source_folder_path + '\\' + file)
                dest_mod_time = os.path.getmtime(self.dest_folder_path + '\\' + file)

                if source_mod_time > dest_mod_time:
                    files_to_copy.append(file)
                    

            if len(files_to_copy) > 0:
                self.iterate_copy_files(files_to_copy)
                
                # Lets print out a summary of what we did
                print('\n')
                self.live_output.console.rule(f'Job ID: {self.id} | {self.source} -> {self.dest}', style="bold green")
                print('\n')
                print(f'🆕 New files found: {files_to_copy}')
                print(f'✅ Successfully completed watching job {self.id}. {self.files_copied} file(s) were copied.')
                self.live_output.console.rule('.')
                print('\n')

            else:
                print(f'Job ID: {self.id}. Source and destination directories are the same. Not copying files this time.')
        else:
            self.live_output.console.log('❌ No connection to the source or destination host could be made, are they online?')

        # When the job thread has completed its running, signal the file master to remove it from the active list 
        self.parent.on_job_finish(self.id, len(files_to_copy))


    def generate_connection(self, host, domain, username, password):
        """
        Handles the logic for creating a connection. Cancels a connection if the already in use error is first returned.
        """
        source_connection = create_wnet_connection(host, domain, username, password)
        if source_connection['outcome'] == 'cancel':
            source_cancel = remove_wnet_connection(host)
            source_connection = create_wnet_connection(host, domain, username, password)

        if source_connection['outcome'] == 'error':
            return {'outcome': 'error'}

        # print(f'Connection to {host} established')
        return {'outcome': 'success'}

    def iterate_copy_files(self, new_files):
         # Copy across the new files
        for file in new_files:
            result = copy_file(self.source_folder_path + '\\' + file, self.dest_folder_path + '\\' + file)
            
            if result['outcome'] == 'success':
                print(f'File successfully copied: {file}')
                # Complete checksum of files
                source_checksum = make_checksum(self.source_folder_path + '\\' + file)
                dest_checksum = make_checksum(self.dest_folder_path + '\\' + file)

                if verify_checksums(source_checksum, dest_checksum):
                    self.files_copied += 1
                    #print(f'Checksum confirmed between source and dest file: {file}')
                else:
                    print(f'ERROR: checksum does not match for file: {file}')


if __name__ == '__main__':
    app = FileWatcher(parameters_path='parameters.json')
    with Live(app.print_timers_table(), refresh_per_second=2) as live:
        app.set_live_output(live)
        while app.running:
            app.timer_countdown()
            live.update(app.print_timers_table())
            time.sleep(1)