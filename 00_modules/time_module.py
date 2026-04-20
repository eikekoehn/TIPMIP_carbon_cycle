class Timer:
        
    def adjust_time_axes(da,freq_input,freq_output):
        # now deal with the temporal frequency
        if freq_output == freq_input:
            print('No need to transform the temporal coordinates.')
            if freq_input == 'daily':
                print('We only make sure that the time axes are cftime.Gregorian with the time stamp at the beginning of each day.')
                print('to implement')
            elif freq_input == 'monthly':
                print('We only make sure that the time axes are cftime.Gregorian with the time stamp at the beginning of each month.')
                print('to implement')
            elif freq_input == 'yearly':
                print('We only make sure that the time axes are cftime.Gregorian with the time stamp at the beginning of each year.')
                print('to implement')

