"""
Equipment repository for VoltMetrics.

This module provides data access methods for equipment.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from models.equipment import Equipment, EquipmentType


class EquipmentRepository:
    """
    Repository for accessing equipment data in the database.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def get_all(self) -> List[Equipment]:
        """
        Retrieve all equipment.
        
        Returns:
            List of all Equipment objects
        """
        return self.db.query(Equipment).all()
    
    def get_by_id(self, equipment_id: str) -> Optional[Equipment]:
        """
        Get equipment by its ID.
        
        Args:
            equipment_id: Equipment ID to lookup
            
        Returns:
            Equipment object if found, None otherwise
        """
        return self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
    
    def get_by_facility(self, facility_id: str) -> List[Equipment]:
        """
        Get all equipment for a specific facility.
        
        Args:
            facility_id: Facility ID to lookup equipment for
            
        Returns:
            List of Equipment objects
        """
        return self.db.query(Equipment).filter(Equipment.facility_id == facility_id).all()
    
    def get_by_type(self, equipment_type: EquipmentType) -> List[Equipment]:
        """
        Get all equipment of a specific type.
        
        Args:
            equipment_type: EquipmentType to filter by
            
        Returns:
            List of Equipment objects
        """
        return self.db.query(Equipment).filter(Equipment.type == equipment_type).all()
    
    def get_with_maintenance(self, equipment_id: str) -> Optional[Equipment]:
        """
        Get equipment with maintenance records eagerly loaded.
        
        Args:
            equipment_id: Equipment ID to lookup
            
        Returns:
            Equipment object with maintenance records if found, None otherwise
        """
        return self.db.query(Equipment).filter(Equipment.id == equipment_id).options(
            joinedload(Equipment.maintenance_records)
        ).first()
    
    def get_without_maintenance_since(self, date: datetime) -> List[Equipment]:
        """
        Get equipment that hasn't had maintenance since the given date.
        
        Args:
            date: Date to check against
            
        Returns:
            List of Equipment objects with no maintenance since the date
        """
        return self.db.query(Equipment).filter(
            (Equipment.last_maintenance_date == None) | 
            (Equipment.last_maintenance_date < date)
        ).all()
    
    def get_oldest_equipment(self, limit: int = 10) -> List[Equipment]:
        """
        Get the oldest equipment based on installation date.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of Equipment objects ordered by installation date (oldest first)
        """
        return self.db.query(Equipment).order_by(Equipment.installation_date).limit(limit).all()
    
    def create(self, equipment: Equipment) -> Equipment:
        """
        Create a new equipment record in the database.
        
        Args:
            equipment: Equipment object to create
            
        Returns:
            Created Equipment with ID
        """
        self.db.add(equipment)
        self.db.commit()
        self.db.refresh(equipment)
        return equipment
    
    def update(self, equipment: Equipment) -> Equipment:
        """
        Update an existing equipment record.
        
        Args:
            equipment: Equipment object with updated values
            
        Returns:
            Updated Equipment
        """
        self.db.merge(equipment)
        self.db.commit()
        return equipment
    
    def delete(self, equipment_id: str) -> bool:
        """
        Delete an equipment record by ID.
        
        Args:
            equipment_id: ID of equipment to delete
            
        Returns:
            True if deleted, False if not found
        """
        equipment = self.get_by_id(equipment_id)
        if not equipment:
            return False
        
        self.db.delete(equipment)
        self.db.commit()
        return True 