import collections
import time

MEMORY_RESET_THRESHOLD = 0.1
Coefficients = collections.namedtuple('Coefficients', ['kP', 'kI', 'kD'])

def sign_function(x):
        return 1 if x > 0 else 0 if x == 0 else -1

class PIDController():
    """
    General PID controller object
    """

    _magnitudes = { "p": 0, "i": 0, "d": 0 }

    _last_error = 0
    _clamp = False
    _last_compute_timestamp = 0

    def __init__(self, kP=1, kI=0, kD=0.5, saturation_limit_max=15, saturation_limit_min=-15):
        self._coefficients = Coefficients(kP, kI, kD)
        self._saturation_limit_max = saturation_limit_max
        self._saturation_limit_min = saturation_limit_min

    def _pid(self):
        """
        private method used to compute the overall pid value
        """
        return self._coefficients.kP * self._magnitudes["p"] + \
            self._coefficients.kI * self._magnitudes["i"] + \
                self._coefficients.kD * self._magnitudes["d"]
    
    def generate_value(self, error):
        """
        Generates the next PID output using a provided error
        """
        # generate timestamps for estimating rates of change
        timestamp = time.time()
        time_delta = timestamp - self._last_compute_timestamp / 1000

        self._magnitudes["p"] = error

        # reset the memory time if the time delta is too high (> 0.1 second)
        if(time_delta > MEMORY_RESET_THRESHOLD):
            self._magnitudes["d"] = 0
        else:
            self._magnitudes["d"] = (error - self._last_error) / time_delta;

        # accumulate the integral value if the clamp is inactive
        if(not self._clamp):
            self._magnitudes["i"] = self._magnitudes["i"] + error * time_delta;

        self._last_error = error
        pre_saturation_pid_value = self._pid()
        # clamp the value with the provided saturation limits
        post_saturation_pid_value = min(max(pre_saturation_pid_value, self._saturation_limit_min), self._saturation_limit_max)

        # activate the clamp if any of the saturation values have been reached
        if(pre_saturation_pid_value != post_saturation_pid_value):
            if(sign_function(self._last_error) == sign_function(post_saturation_pid_value)):
                self._clamp = True
            else:
                self._clamp = False
        else:
            self._clamp = False

        self._last_compute_timestamp = timestamp

        return post_saturation_pid_value