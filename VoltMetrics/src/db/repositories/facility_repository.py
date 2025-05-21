"""
Facility repository for VoltMetrics.

This module provides data access methods for facilities.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from models.facility import Facility


class FacilityRepository:
    """
    Repository for accessing facility data in the database.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def get_all(self) -> List[Facility]:
        """
        Retrieve all facilities.
        
        Returns:
            List of all Facility objects
        """
        return self.db.query(Facility).all()
    
    def get_by_id(self, facility_id: str) -> Optional[Facility]:
        """
        Get a facility by its ID.
        
        Args:
            facility_id: Facility ID to lookup
            
        Returns:
            Facility object if found, None otherwise
        """
        return self.db.query(Facility).filter(Facility.id == facility_id).first()
    
    def get_with_equipment(self, facility_id: str) -> Optional[Facility]:
        """
        Get a facility with all its equipment eagerly loaded.
        
        Args:
            facility_id: Facility ID to lookup
            
        Returns:
            Facility object with equipment if found, None otherwise
        """
        return self.db.query(Facility).filter(Facility.id == facility_id).options(
            joinedload(Facility.equipment)
        ).first()
    
    def create(self, facility: Facility) -> Facility:
        """
        Create a new facility in the database.
        
        Args:
            facility: Facility object to create
            
        Returns:
            Created Facility with ID
        """
        self.db.add(facility)
        self.db.commit()
        self.db.refresh(facility)
        return facility
    
    def update(self, facility: Facility) -> Facility:
        """
        Update an existing facility.
        
        Args:
            facility: Facility object with updated values
            
        Returns:
            Updated Facility
        """
        self.db.merge(facility)
        self.db.commit()
        return facility
    
    def delete(self, facility_id: str) -> bool:
        """
        Delete a facility by ID.
        
        Args:
            facility_id: ID of facility to delete
            
        Returns:
            True if deleted, False if not found
        """
        facility = self.get_by_id(facility_id)
        if not facility:
            return False
        
        self.db.delete(facility)
        self.db.commit()
        return True 