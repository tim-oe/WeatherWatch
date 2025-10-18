#!/usr/bin/env python3
"""
AS3935 Lightning Sensor Test Simulator
Simulates lightning events for testing the sensor module
"""

__all__ = ["LightningSimulator", "AS3935TesterUtil"]

import random
import threading
import time
from datetime import datetime

import RPi.GPIO as GPIO


class LightningSimulator:
    """Simulate lightning events for AS3935 sensor testing"""

    def __init__(self, test_pin: int = 18):
        """
        Initialize lightning simulator

        Args:
            test_pin: GPIO pin to use for generating test pulses
                     (different from sensor's IRQ pin)
        """
        self.test_pin = test_pin
        self.running = False
        self.sim_thread = None

        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.test_pin, GPIO.OUT, initial=GPIO.HIGH)

    def _generate_pulse(self, duration_ms: float = 2.0):
        """Generate a falling edge pulse to simulate interrupt"""
        if GPIO:
            GPIO.output(self.test_pin, GPIO.LOW)
            time.sleep(duration_ms / 1000.0)
            GPIO.output(self.test_pin, GPIO.HIGH)
        else:
            print(f"MOCK: Generated {duration_ms}ms pulse on pin {self.test_pin}")

    def simulate_lightning_strike(self):
        """Simulate a single lightning strike"""
        print("⚡ Simulating lightning strike...")
        self._generate_pulse(2.0)
        time.sleep(0.1)

    def simulate_disturber(self):
        """Simulate an electrical disturber"""
        print("🔧 Simulating electrical disturber...")
        self._generate_pulse(1.0)
        time.sleep(0.1)

    def simulate_noise_burst(self):
        """Simulate noise interference"""
        print("📢 Simulating noise burst...")
        # Multiple short pulses for noise
        for _ in range(3):
            self._generate_pulse(0.5)
            time.sleep(0.05)
        time.sleep(0.1)

    def run_test_sequence(self):
        """Run a comprehensive test sequence"""
        print("🧪 Starting AS3935 test sequence...")
        print("=" * 50)

        test_events = [
            ("Lightning Strike 1", self.simulate_lightning_strike),
            ("Noise Burst", self.simulate_noise_burst),
            ("Electrical Disturber", self.simulate_disturber),
            ("Lightning Strike 2", self.simulate_lightning_strike),
            ("Lightning Strike 3", self.simulate_lightning_strike),
            ("Final Noise Test", self.simulate_noise_burst),
        ]

        for i, (name, test_func) in enumerate(test_events, 1):
            print(f"Test {i}/6: {name}")
            test_func()
            time.sleep(2)  # Wait between tests

        print("=" * 50)
        print("✅ Test sequence completed!")

    def start_random_simulation(self, interval_range: tuple = (5, 15)):
        """
        Start random event simulation

        Args:
            interval_range: Min/max seconds between events
        """
        if self.running:
            print("Simulation already running")
            return

        self.running = True
        self.sim_thread = threading.Thread(target=self._random_simulation_loop, args=(interval_range,))
        self.sim_thread.daemon = True
        self.sim_thread.start()
        print(f"🎲 Started random simulation (every {interval_range[0]}-{interval_range[1]}s)")

    def _random_simulation_loop(self, interval_range: tuple):
        """Random simulation loop"""
        events = [
            ("Lightning", self.simulate_lightning_strike, 0.6),  # 60% chance
            ("Disturber", self.simulate_disturber, 0.25),  # 25% chance
            ("Noise", self.simulate_noise_burst, 0.15),  # 15% chance
        ]

        while self.running:
            # Random interval
            wait_time = random.uniform(*interval_range)
            time.sleep(wait_time)

            if not self.running:
                break

            # Choose random event based on probabilities
            rand_val = random.random()
            cumulative = 0

            for event_name, event_func, probability in events:
                cumulative += probability
                if rand_val <= cumulative:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] Random {event_name}")
                    event_func()
                    break

    def stop_simulation(self):
        """Stop random simulation"""
        if not self.running:
            return

        self.running = False
        if self.sim_thread:
            self.sim_thread.join(timeout=2)
        print("🛑 Simulation stopped")

    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop_simulation()
        if GPIO:
            GPIO.cleanup()


class AS3935TesterUtil:
    """Utility class for testing AS3935 sensor responses"""

    def __init__(self, sensor_module, simulator: LightningSimulator):
        """
        Initialize tester

        Args:
            sensor_module: Your AS3935LightningSensor instance
            simulator: LightningSimulator instance
        """
        self.sensor = sensor_module
        self.simulator = simulator
        self.test_results = []

    def setup_test_callbacks(self):
        """Setup callbacks to capture test results"""

        def on_test_lightning(event):
            result = {"timestamp": event.timestamp, "type": "lightning", "distance": event.distance, "energy": event.energy}
            self.test_results.append(result)
            print(f"✅ CAPTURED: Lightning - Distance: {event.distance}km, Energy: {event.energy}")

        def on_test_disturber(event):
            result = {"timestamp": event.timestamp, "type": "disturber"}
            self.test_results.append(result)
            print("✅ CAPTURED: Disturber")

        def on_test_noise(event):
            result = {"timestamp": event.timestamp, "type": "noise", "noise_level": event.noise_level}
            self.test_results.append(result)
            print(f"✅ CAPTURED: Noise - Level: {event.noise_level}")

        # Subscribe to events
        self.sensor.subscribe_to_events("lightning_detected", on_test_lightning)
        self.sensor.subscribe_to_events("disturber_detected", on_test_disturber)
        self.sensor.subscribe_to_events("noise_detected", on_test_noise)

    def run_comprehensive_test(self):
        """Run comprehensive sensor test"""
        print("🔬 Starting comprehensive AS3935 test...")

        # Clear previous results
        self.test_results.clear()

        # Setup callbacks
        self.setup_test_callbacks()

        # Ensure sensor is monitoring
        if not self.sensor.running:
            self.sensor.start_monitoring()

        # Run test sequence
        self.simulator.run_test_sequence()

        # Wait for events to process
        time.sleep(3)

        # Report results
        self._report_test_results()

    def _report_test_results(self):
        """Report test results"""
        print("\n📊 TEST RESULTS")
        print("=" * 40)

        if not self.test_results:
            print("❌ No events captured - check connections")
            return

        event_counts = {}
        for result in self.test_results:
            event_type = result["type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        for event_type, count in event_counts.items():
            print(f"{event_type.capitalize()}: {count} events")

        print(f"\nTotal events captured: {len(self.test_results)}")
        print("=" * 40)


# Example usage functions
def manual_test_example():
    """Manual testing example"""
    simulator = LightningSimulator(test_pin=18)

    try:
        print("Manual AS3935 Testing")
        print("Commands:")
        print("  l - Lightning strike")
        print("  d - Disturber")
        print("  n - Noise burst")
        print("  s - Test sequence")
        print("  q - Quit")
        print("-" * 30)

        while True:
            cmd = input("Enter command: ").lower().strip()

            if cmd == "l":
                simulator.simulate_lightning_strike()
            elif cmd == "d":
                simulator.simulate_disturber()
            elif cmd == "n":
                simulator.simulate_noise_burst()
            elif cmd == "s":
                simulator.run_test_sequence()
            elif cmd == "q":
                break
            else:
                print("Unknown command")

    except KeyboardInterrupt:
        pass
    finally:
        simulator.cleanup()


def automatic_test_example():
    """Automatic testing example"""
    simulator = LightningSimulator(test_pin=18)

    try:
        # Start random simulation
        simulator.start_random_simulation(interval_range=(3, 8))

        print("Automatic testing started...")
        print("Press Ctrl+C to stop")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        simulator.cleanup()


if __name__ == "__main__":
    print("AS3935 Lightning Sensor Test Simulator")
    print("Choose test mode:")
    print("1. Manual testing")
    print("2. Automatic random testing")
    print("3. Exit")

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        manual_test_example()
    elif choice == "2":
        automatic_test_example()
    else:
        print("Exiting...")
