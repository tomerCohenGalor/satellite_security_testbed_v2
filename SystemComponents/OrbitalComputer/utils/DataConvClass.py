class DataConv:
    def __init__(self):
        print('init')
        
    def cleanup(self):
        print('cleanup')

    @staticmethod
    def get_satellite(self):
        print('get_satellite')
    
    def process_solar_intensity(self, solar_intensity, scale):
        print('process_solar_intensity')


    def convert_magnetic_field(self, magnetic_field):
        print("convert_magnetic_field")
        
    def output_to_daq(self, analog_data, digital_data):
        print('output_to_daq')

    def process_magnetic_fields(self, row_data):
        print('process_magnetic_fields')

    def deserialize_time(self, time_tuple):
        return self.ts.utc(*time_tuple)

    def start(self):
        print("Starting the dataConv client... and run it and connect to manager")

        print("Sending prep messages...")
        print("While true loop communicating with the manager")
            
    
            
    def play_satellite_view_video(self, video_path, is_demo_running):
        print("Playing video")