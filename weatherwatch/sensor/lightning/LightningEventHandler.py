from typing import Dict

from sensor.lightning.LightningEvent import LightningEvent

__all__ = ["LightningEventHandler"]


class LightningEventHandler:
    """Example event handler for lightning events"""

    def __init__(self):
        self.lightning_count = 0
        self.disturber_count = 0
        self.noise_count = 0

    def on_lightning_detected(self, event: LightningEvent):
        """Handle lightning detection events"""
        self.lightning_count += 1
        print(f"⚡ LIGHTNING DETECTED! #{self.lightning_count}")
        print(f"   Time: {event.timestamp}")
        print(f"   Distance: {event.distance}km")
        print(f"   Energy: {event.energy}")
        print(f"   JSON: {event.to_json()}")
        print("-" * 50)

    def on_disturber_detected(self, event: LightningEvent):
        """Handle disturber detection events"""
        self.disturber_count += 1
        print(f"🔧 DISTURBER DETECTED! #{self.disturber_count}")
        print(f"   Time: {event.timestamp}")
        print("-" * 50)

    def on_noise_detected(self, event: LightningEvent):
        """Handle noise detection events"""
        self.noise_count += 1
        print(f"📢 NOISE DETECTED! #{self.noise_count}")
        print(f"   Time: {event.timestamp}")
        print(f"   Noise Level: {event.noise_level}")
        print("-" * 50)

    def get_statistics(self) -> Dict[str, int]:
        """Get event statistics"""
        return {
            "lightning_events": self.lightning_count,
            "disturber_events": self.disturber_count,
            "noise_events": self.noise_count,
        }
