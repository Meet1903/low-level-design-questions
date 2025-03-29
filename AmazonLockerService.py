from enum import Enum
import math
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

class LockerSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class LockerStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    OCCUPIED = 'OCCUPIED'
    MAINTAINANCE = 'MAINTANANCE'

class DeliveryStatus(Enum):
    PENDING = 'PENDING'
    DELIVERED = 'DELIVERED'
    PICKED_UP = 'PICKED_UP'
    EXPIRED = 'EXPIRED'

class GeoLocation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    
    def distance_to(self, other: 'GeoLocation') -> float:
        R = 6371  # Earth's radius in kilometers

        # Convert latitude and longitude to radians
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

class Locker():
    def __init__(self, locker_id, size, location):
        self.locker_id = locker_id
        self.location = location
        self.size = size
        self.status = LockerStatus.AVAILABLE
        self.current_package = None
    
    def is_exact_match(self, package_size):
        return self.size == package_size

    def can_fit(self, package_size):
        return self.size.value >= package_size

    def assign_package(self, package):
        if self.status == LockerStatus.AVAILABLE and self.can_fit(package.size):
            self.status = LockerStatus.OCCUPIED
            self.current_package = package
            return True
        return False
    
    def release_package(self):
        if self.status == LockerStatus.OCCUPIED:
            self.status = LockerStatus.AVAILABLE
            self.current_package = None
            return True
        return False

class Package():
    def __init__(self, package_id, tracking_number, recipient_phone, size, delivery_partner, user_location: GeoLocation):
        self.tracking_number = tracking_number
        self.recipient_phone = recipient_phone
        self.size = size
        self.delivery_partner = delivery_partner
        self.user_lcoation = user_location
        self.delivery_code = self._generate_delivery_code()
        self.status = DeliveryStatus.PENDING
        self.delivery_time = datetime.now()
        self.expiry_time = datetime.now() + timedelta(days = 3)
    
    def _generate_delivery_code(self):
        return str(uuid.uuid4())[:6].upper()

class LockerStation:
    def __init__(self, station_id, location, geo_location):
        self.station_id = station_id
        self.location = location
        self.geo_location: GeoLocation = geo_location
        self.lockers: Dict[str, Locker]= {}
    
    def add_locker(self, locker: Locker):
        self.lockers[locker.locker_id] = locker
    
    def find_available_locker(self, package_size):

        for locker in self.lockers.values():
            if locker.status == LockerStatus.AVAILABLE and locker.size == package_size:
                return locker
        
        for locker in self.lockers.values():
            if locker.status == LockerStatus.AVAILABLE and locker.can_fit(package_size):
                return locker
        
        return None

class LockerService:
    def __init__(self):
        self.locker_stations: Dict[str, LockerStation] = {}
        self.active_packages: Dict[str, Package] = {}
        self.active_lockers: Dict[str, Locker]= {}

    def create_locaker_station(self, station_id, location, geo_location) -> LockerStation:
        station = LockerStation(station_id, location, geo_location)
        self.locker_stations[station_id] = station
        return station
    
    def find_nearest_location_station(self, user_location):
        nearest_station = None
        min_distance = float('inf')

        for station in self.locker_stations.values():
            distance = station.geo_location.distance_to(user_location)
            if distance < min_distance:
                nearest_station = station
                min_distance = distance
        return nearest_station

    def deliver_package(self, package: Package) -> Locker:
        nearest_station = self.find_nearest_location_station(package.user_lcoation)

        if nearest_station:
            available_locker = nearest_station.find_available_locker(package_size=package.size)

            if available_locker:
                self.active_packages[package.tracking_number] = package
                self.active_lockers[package.tracking_number] = available_locker
                return True
        return False

    def pickup_package(self, tracking_number, deliver_code):
        if tracking_number in self.active_packages:
            package = self.active_packages[tracking_number]
            if package.delivery_code == deliver_code:
                self.active_lockers[tracking_number].release_package()
                del self.active_lockers[tracking_number]
                del self.active_packages[tracking_number]
        return package


if __name__=='__main__':
    locker_service = LockerService()

    station = locker_service.create_locaker_station("STATION_1", "Brooklyn", GeoLocation(0.7128, -74.0060))

    station.add_locker(Locker('Locker1', LockerSize.SMALL, "Brooklyn"))
    station.add_locker(Locker('Locker2', LockerSize.MEDIUM, "Brooklyn"))
    station.add_locker(Locker('Locker3', LockerSize.LARGE, "Brooklyn"))
    station.add_locker(Locker('Locker4', LockerSize.SMALL, "Brooklyn"))

    user_location = GeoLocation(40.7212, -74.0022)
    small_package = Package("P1", "AMZN1234", "+1234567", LockerSize.SMALL, 'Amazon', user_location)

    delivery_status = locker_service.deliver_package(small_package)

    package = locker_service.pickup_package("AMZN1234", "123456780") #Number is sent via notification




