from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid

class VehicleType(Enum):
    SEDAN = "Sedan"
    SUV = "SUV"
    HATCHBACK = "Hatchback"
    LUXURY = "Luxury"
    TRUCK = "Truck"

class ReservationStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class PaymentStatus(Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"


class User:
    def __init__(self, user_id: str, name: str, email: str, phone: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.reservations: List[Reservation] = []

    def create_reservation(self, vehicle: 'Vehicle', start_date: datetime, end_date: datetime) -> 'Reservation':
        reservation = Reservation(self, vehicle, start_date, end_date)
        self.reservations.append(reservation)
        return reservation

    def cancel_reservation(self, reservation: 'Reservation'):
        if reservation in self.reservations:
            reservation.cancel()

class Vehicle(ABC):
    def __init__(self, vehicle_id: str, license_plate: str, vehicle_type: VehicleType, 
                 make: str, model: str, year: int, daily_rate: float):
        self.vehicle_id = vehicle_id
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        self.make = make
        self.model = model
        self.year = year
        self.daily_rate = daily_rate
        self.is_available = True
        self.current_reservation: Optional['Reservation'] = None

    @abstractmethod
    def calculate_rental_cost(self, start_date: datetime, end_date: datetime) -> float:
        pass

    def mark_available(self):
        self.is_available = True
        self.current_reservation = None

    def mark_unavailable(self, reservation: 'Reservation'):
        self.is_available = False
        self.current_reservation = reservation

class StandardVehicle(Vehicle):
    def calculate_rental_cost(self, start_date: datetime, end_date: datetime) -> float:
        rental_days = (end_date - start_date).days + 1
        return self.daily_rate * rental_days

class LuxuryVehicle(Vehicle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daily_rate *= 1.5 

    def calculate_rental_cost(self, start_date: datetime, end_date: datetime) -> float:
        rental_days = (end_date - start_date).days + 1
        return self.daily_rate * rental_days
    
class Reservation:
    def __init__(self, user: User, vehicle: Vehicle, 
                 start_date: datetime, end_date: datetime):
        self.reservation_id = str(uuid.uuid4())
        self.user = user
        self.vehicle = vehicle
        self.start_date = start_date
        self.end_date = end_date
        self.status = ReservationStatus.CONFIRMED
        self.total_cost = vehicle.calculate_rental_cost(start_date, end_date)
        
        # Mark vehicle as unavailable
        vehicle.mark_unavailable(self)

    def cancel(self):
        if self.status == ReservationStatus.CONFIRMED:
            self.status = ReservationStatus.CANCELLED
            self.vehicle.mark_available()

    def complete(self):
        self.status = ReservationStatus.COMPLETED
        self.vehicle.mark_available()

class Payment:
    def __init__(self, reservation: Reservation, amount: float):
        self.payment_id = str(uuid.uuid4())
        self.reservation = reservation
        self.amount = amount
        self.status = PaymentStatus.PENDING
        self.payment_date = datetime.now()

    def process_payment(self, payment_method: str) -> bool:
        # Simulated payment processing
        try:
            # In a real system, this would integrate with a payment gateway
            self.status = PaymentStatus.COMPLETED
            return True
        except Exception:
            self.status = PaymentStatus.FAILED
            return False

class CarRentalSystem:
    def __init__(self):
        self.vehicles: Dict[str, Vehicle] = {}
        self.users: Dict[str, User] = {}
        self.active_reservations: List[Reservation] = []

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles[vehicle.vehicle_id] = vehicle

    def register_user(self, user: User):
        self.users[user.user_id] = user

    def search_available_vehicles(self, 
                                  vehicle_type: Optional[VehicleType] = None, 
                                  start_date: Optional[datetime] = None, 
                                  end_date: Optional[datetime] = None) -> List[Vehicle]:
        available_vehicles = []
        for vehicle in self.vehicles.values():
            if vehicle.is_available:
                # Additional filtering can be added here
                if vehicle_type and vehicle.vehicle_type != vehicle_type:
                    continue
                available_vehicles.append(vehicle)
        return available_vehicles

    def create_reservation(self, user: User, vehicle: Vehicle, 
                           start_date: datetime, end_date: datetime) -> Reservation:
        # Additional validation can be added here
        reservation = user.create_reservation(vehicle, start_date, end_date)
        self.active_reservations.append(reservation)
        return reservation
    
if __name__ == "__main__":
    rental_system = CarRentalSystem()

    sedan1 = StandardVehicle(
        vehicle_id="V001", 
        license_plate="ABC123", 
        vehicle_type=VehicleType.SEDAN, 
        make="Toyota", 
        model="Camry", 
        year=2022, 
        daily_rate=50.0
    )
    rental_system.add_vehicle(sedan1)

    user = User(
        user_id="U001", 
        name="John Doe", 
        email="john@example.com", 
        phone="1234567890"
    )
    rental_system.register_user(user)

    start_date = datetime.now()
    end_date = start_date + timedelta(days=3)
    reservation = rental_system.create_reservation(user, sedan1, start_date, end_date)

    payment = Payment(reservation, reservation.total_cost)
    payment.process_payment("Credit Card")