#!/usr/bin/env python3
"""
Grove Lightning Sensor (AS3935) Module for Raspberry Pi
Integrates with python_event_bus for real-time lightning detection events

Requirements:
- python_event_bus
- RPi.GPIO
- smbus2 (for I2C communication)

Hardware connections:
- VCC: 3.3V or 5V
- GND: Ground
- SDA: GPIO 2 (I2C SDA)
- SCL: GPIO 3 (I2C SCL)
- IRQ: GPIO 4 (configurable)
"""

import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import RPi.GPIO as GPIO
import smbus2

# from py_singleton import singleton
from python_event_bus import EventBus
from sensor.lightning.LightningEvent import LightningEvent
from util.Logger import logger

__all__ = ["AS3935Reader"]


@logger
# @singleton
class AS3935Reader:
    """
    Grove Lightning Sensor (AS3935) driver for Raspberry Pi
    Supports I2C communication and interrupt-based detection
    """

    # AS3935 I2C address
    I2C_ADDRESS = 0x2D

    # Register addresses
    REG_AFE_GAIN = 0x00
    REG_POWER_DOWN = 0x00
    REG_NOISE_LEVEL = 0x01
    REG_WATCHDOG_THRESHOLD = 0x01
    REG_SPIKE_REJECTION = 0x02
    REG_LIGHTNING_THRESHOLD = 0x02
    REG_LIGHTNING_REG = 0x03
    REG_ENERGY_LIGHT_LSB = 0x04
    REG_ENERGY_LIGHT_MSB = 0x05
    REG_ENERGY_LIGHT_MMSB = 0x06
    REG_DISTANCE = 0x07
    REG_DISP_FLAGS = 0x08
    REG_CALIB_TRCO = 0x3A
    REG_CALIB_SRCO = 0x3B
    REG_PRESET_DEFAULT = 0x3C
    REG_CALIB_RCO = 0x3D

    # Interrupt types
    INT_NOISE = 0x01
    INT_DISTURBER = 0x04
    INT_LIGHTNING = 0x08

    def __init__(
        self,
        i2c_bus: int = 1,
        irq_pin: int = 3,
        indoor: bool = True,
        noise_level: int = 2,
        watchdog_threshold: int = 2,
        spike_rejection: int = 2,
    ):
        """
        Initialize the AS3935 lightning sensor

        Args:
            i2c_bus: I2C bus number (default: 1)
            irq_pin: GPIO pin for interrupt (default: 4)
            indoor: True for indoor use, False for outdoor
            noise_level: Noise level threshold (0-7)
            watchdog_threshold: Watchdog threshold (0-15)
            spike_rejection: Spike rejection threshold (0-15)
        """
        self.i2c_bus = i2c_bus
        self.irq_pin = irq_pin
        self.indoor = indoor
        self.noise_level = noise_level
        self.watchdog_threshold = watchdog_threshold
        self.spike_rejection = spike_rejection

        self.bus = None
        self.event_bus = EventBus()
        self.running = False
        self.monitor_thread = None

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.irq_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._initialize_sensor()

    def _initialize_sensor(self):
        """Initialize the AS3935 sensor with default settings"""
        try:
            self.bus = smbus2.SMBus(self.i2c_bus)

            # Reset to default settings
            self.bus.write_byte_data(self.I2C_ADDRESS, self.REG_PRESET_DEFAULT, 0x96)
            time.sleep(0.002)  # 2ms delay

            # Configure for indoor/outdoor use
            if self.indoor:
                self._set_indoor()
            else:
                self._set_outdoor()

            # Set noise level
            self._set_noise_level(self.noise_level)

            # Set watchdog threshold
            self._set_watchdog_threshold(self.watchdog_threshold)

            # Set spike rejection
            self._set_spike_rejection(self.spike_rejection)

            # Clear statistics
            self._clear_statistics()

            self.logger.info("AS3935 Lightning Sensor initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize AS3935 sensor: {e}")
            raise

    def _read_register(self, register: int) -> int:
        """Read a register from the AS3935"""
        return self.bus.read_byte_data(self.I2C_ADDRESS, register)

    def _write_register(self, register: int, value: int):
        """Write a value to a register"""
        self.bus.write_byte_data(self.I2C_ADDRESS, register, value)

    def _set_indoor(self):
        """Configure sensor for indoor use"""
        reg_val = self._read_register(self.REG_AFE_GAIN)
        reg_val |= 0x20  # Set AFE_GB bit
        self._write_register(self.REG_AFE_GAIN, reg_val)

    def _set_outdoor(self):
        """Configure sensor for outdoor use"""
        reg_val = self._read_register(self.REG_AFE_GAIN)
        reg_val &= ~0x20  # Clear AFE_GB bit
        self._write_register(self.REG_AFE_GAIN, reg_val)

    def _set_noise_level(self, level: int):
        """Set noise level threshold (0-7)"""
        if not 0 <= level <= 7:
            raise ValueError("Noise level must be between 0 and 7")

        reg_val = self._read_register(self.REG_NOISE_LEVEL)
        reg_val = (reg_val & 0x8F) | ((level & 0x07) << 4)
        self._write_register(self.REG_NOISE_LEVEL, reg_val)

    def _set_watchdog_threshold(self, threshold: int):
        """Set watchdog threshold (0-15)"""
        if not 0 <= threshold <= 15:
            raise ValueError("Watchdog threshold must be between 0 and 15")

        reg_val = self._read_register(self.REG_WATCHDOG_THRESHOLD)
        reg_val = (reg_val & 0xF0) | (threshold & 0x0F)
        self._write_register(self.REG_WATCHDOG_THRESHOLD, reg_val)

    def _set_spike_rejection(self, rejection: int):
        """Set spike rejection threshold (0-15)"""
        if not 0 <= rejection <= 15:
            raise ValueError("Spike rejection must be between 0 and 15")

        reg_val = self._read_register(self.REG_SPIKE_REJECTION)
        reg_val = (reg_val & 0xF0) | (rejection & 0x0F)
        self._write_register(self.REG_SPIKE_REJECTION, reg_val)

    def _clear_statistics(self):
        """Clear lightning statistics"""
        reg_val = self._read_register(self.REG_LIGHTNING_REG)
        reg_val |= 0x40  # Set CL_STAT bit
        self._write_register(self.REG_LIGHTNING_REG, reg_val)
        reg_val &= ~0x40  # Clear CL_STAT bit
        self._write_register(self.REG_LIGHTNING_REG, reg_val)

    def _get_interrupt_source(self) -> int:
        """Get the interrupt source"""
        return self._read_register(self.REG_LIGHTNING_REG) & 0x0F

    def _get_lightning_distance(self) -> Optional[int]:
        """Get lightning distance in km"""
        distance = self._read_register(self.REG_DISTANCE) & 0x3F
        if distance == 0x3F:
            return None  # Out of range
        return distance

    def _get_lightning_energy(self) -> int:
        """Get lightning energy level"""
        lsb = self._read_register(self.REG_ENERGY_LIGHT_LSB)
        msb = self._read_register(self.REG_ENERGY_LIGHT_MSB)
        mmsb = self._read_register(self.REG_ENERGY_LIGHT_MMSB)
        return (mmsb << 16) | (msb << 8) | lsb

    def _get_noise_level(self) -> int:
        """Get current noise level"""
        return (self._read_register(self.REG_NOISE_LEVEL) >> 4) & 0x07

    def _handle_interrupt(self):
        """Handle interrupt from AS3935"""
        time.sleep(0.003)  # Wait 3ms for interrupt to settle

        int_source = self._get_interrupt_source()
        timestamp = datetime.now()

        if int_source == self.INT_LIGHTNING:
            # Lightning detected
            distance = self._get_lightning_distance()
            energy = self._get_lightning_energy()

            event = LightningEvent(timestamp=timestamp, event_type="lightning", distance=distance, energy=energy)

            self.logger.info(f"Lightning detected! Distance: {distance}km, Energy: {energy}")
            self.event_bus.emit("lightning_detected", event)

        elif int_source == self.INT_DISTURBER:
            # Disturber detected
            event = LightningEvent(timestamp=timestamp, event_type="disturber")

            self.logger.info("Disturber detected")
            self.event_bus.emit("disturber_detected", event)

        elif int_source == self.INT_NOISE:
            # Noise level too high
            noise_level = self._get_noise_level()
            event = LightningEvent(timestamp=timestamp, event_type="noise", noise_level=noise_level)

            self.logger.info(f"Noise level too high: {noise_level}")
            self.event_bus.emit("noise_detected", event)

    def _monitor_interrupts(self):
        """Monitor for interrupts in a separate thread"""
        self.logger.info("Starting interrupt monitoring...")

        while self.running:
            try:
                # Wait for interrupt (falling edge)
                if GPIO.wait_for_edge(self.irq_pin, GPIO.FALLING, timeout=1000):
                    self._handle_interrupt()
            except Exception as e:
                self.logger.error(f"Error in interrupt monitoring: {e}")
                time.sleep(0.1)

    def start_monitoring(self):
        """Start monitoring for lightning events"""
        if self.running:
            self.logger.warning("Monitoring already started")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_interrupts)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.logger.info("Lightning monitoring started")

    def stop_monitoring(self):
        """Stop monitoring for lightning events"""
        if not self.running:
            self.logger.warning("Monitoring not started")
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        self.logger.info("Lightning monitoring stopped")

    def subscribe_to_events(self, event_type: str, callback: Callable):
        """
        Subscribe to lightning events

        Args:
            event_type: 'lightning_detected', 'disturber_detected', or 'noise_detected'
            callback: Function to call when event occurs
        """
        self.event_bus.subscribe(event_type, callback)

    def unsubscribe_from_events(self, event_type: str, callback: Callable):
        """Unsubscribe from lightning events"""
        self.event_bus.unsubscribe(event_type, callback)

    def get_sensor_info(self) -> Dict[str, Any]:
        """Get current sensor configuration and status"""
        return {
            "i2c_address": hex(self.I2C_ADDRESS),
            "irq_pin": self.irq_pin,
            "indoor_mode": self.indoor,
            "noise_level": self.noise_level,
            "watchdog_threshold": self.watchdog_threshold,
            "spike_rejection": self.spike_rejection,
            "monitoring": self.running,
        }

    def cleanup(self):
        """Clean up resources"""
        self.stop_monitoring()
        if self.bus:
            self.bus.close()
        GPIO.cleanup()
        self.logger.info("AS3935 sensor cleanup completed")
