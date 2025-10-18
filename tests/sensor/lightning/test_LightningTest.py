import time
import unittest

from sensor.lightning.AS3935Reader import AS3935Reader
from sensor.lightning.LightningEventHandler import LightningEventHandler
from sensor.lightning.LightningSimulator import AS3935TesterUtil, LightningSimulator

class LightmimgTest(unittest.TestCase):
    def test(self):        
        # Create sensor instance
        sensor = AS3935Reader(
            i2c_bus=1,
            irq_pin=4,
            indoor=True,  # Set to False for outdoor use
            noise_level=2,
            watchdog_threshold=2,
            spike_rejection=2,
        )

        # Create event handler
        handler = LightningEventHandler()

        # Subscribe to events
        sensor.subscribe_to_events("lightning_detected", handler.on_lightning_detected)
        sensor.subscribe_to_events("disturber_detected", handler.on_disturber_detected)
        sensor.subscribe_to_events("noise_detected", handler.on_noise_detected)

        #simulator = LightningSimulator(test_pin=18)  # Different pin
        #tester = AS3935TesterUtil(sensor, simulator)

        try:
            # Start monitoring
            sensor.start_monitoring()
            #tester.run_comprehensive_test()
            print("Lightning sensor monitoring started...")
            print("Press Ctrl+C to stop")
            print("=" * 50)

            # Keep the program running
            # while True:
            #     time.sleep(1)

        except KeyboardInterrupt:
            print("\nStopping lightning sensor...")

        finally:
            # Clean up
            sensor.cleanup()
            print("Lightning sensor stopped")
