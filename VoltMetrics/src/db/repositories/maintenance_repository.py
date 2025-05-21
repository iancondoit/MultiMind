"""
Maintenance record repository for VoltMetrics.

This module provides data access methods for maintenance records.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.maintenance import MaintenanceRecord


class MaintenanceRepository:
    """
    Repository for accessing maintenance record data in the database.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def get_all(self) -> List[MaintenanceRecord]:
        """
        Retrieve all maintenance records.
        
        Returns:
            List of all MaintenanceRecord objects
        """
        return self.db.query(MaintenanceRecord).all()
    
    def get_by_id(self, record_id: str) -> Optional[MaintenanceRecord]:
        """
        Get a maintenance record by its ID.
        
        Args:
            record_id: Record ID to lookup
            
        Returns:
            MaintenanceRecord object if found, None otherwise
        """
        return self.db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    
    def get_by_equipment(self, equipment_id: str) -> List[MaintenanceRecord]:
        """
        Get all maintenance records for a specific piece of equipment.
        
        Args:
            equipment_id: Equipment ID to lookup records for
            
        Returns:
            List of MaintenanceRecord objects
        """
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.equipment_id == equipment_id
        ).all()
    
    def get_by_equipment_sorted(self, equipment_id: str, limit: int = None) -> List[MaintenanceRecord]:
        """
        Get maintenance records for equipment sorted by date (newest first).
        
        Args:
            equipment_id: Equipment ID to lookup records for
            limit: Maximum number of records to return
            
        Returns:
            List of MaintenanceRecord objects sorted by date
        """
        query = self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.equipment_id == equipment_id
        ).order_by(desc(MaintenanceRecord.date))
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MaintenanceRecord]:
        """
        Get maintenance records within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of MaintenanceRecord objects
        """
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.date >= start_date,
            MaintenanceRecord.date <= end_date
        ).all()
    
    def get_by_type(self, maintenance_type: str) -> List[MaintenanceRecord]:
        """
        Get maintenance records of a specific type.
        
        Args:
            maintenance_type: Type of maintenance to filter by
            
        Returns:
            List of MaintenanceRecord objects
        """
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.type == maintenance_type
        ).all()
    
    def create(self, record: MaintenanceRecord) -> MaintenanceRecord:
        """
        Create a new maintenance record in the database.
        
        Args:
            record: MaintenanceRecord object to create
            
        Returns:
            Created MaintenanceRecord with ID
        """
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def update(self, record: MaintenanceRecord) -> MaintenanceRecord:
        """
        Update an existing maintenance record.
        
        Args:
            record: MaintenanceRecord object with updated values
            
        Returns:
            Updated MaintenanceRecord
        """
        self.db.merge(record)
        self.db.commit()
        return record
    
    def delete(self, record_id: str) -> bool:
        """
        Delete a maintenance record by ID.
        
        Args:
            record_id: ID of record to delete
            
        Returns:
            True if deleted, False if not found
        """
        record = self.get_by_id(record_id)
        if not record:
            return False
        
        self.db.delete(record)
        self.db.commit()
        return True 