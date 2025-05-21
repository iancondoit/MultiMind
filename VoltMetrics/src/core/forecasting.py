"""
Forecasting module for VoltMetrics.

This module implements algorithms for predicting future risk scores and
maintenance needs based on historical data and known risk factors.
"""

from datetime import datetime, timedelta
import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union

from src.models.equipment import Equipment
from src.models.facility import Facility


class RiskForecaster:
    """
    Forecaster for risk trends and predictions.
    
    Implements forecasting algorithms for predicting future equipment and
    facility risk scores based on historical data.
    """
    
    def __init__(self):
        """Initialize the risk forecaster."""
        pass
    
    def forecast_equipment_risk(self, equipment: Equipment, 
                               historical_data: List[Dict[str, Any]],
                               forecast_periods: int = 6,
                               period_months: int = 1) -> Dict[str, Any]:
        """
        Forecast future risk for equipment based on historical data.
        
        Args:
            equipment: Equipment to forecast
            historical_data: List of historical risk assessments
            forecast_periods: Number of periods to forecast
            period_months: Number of months per period
            
        Returns:
            Dictionary with forecast results
        """
        if not historical_data or len(historical_data) < 3:
            return {
                "equipment_id": equipment.id,
                "error": "Insufficient historical data for forecasting",
                "minimum_history_required": 3,
                "history_available": len(historical_data) if historical_data else 0
            }
        
        # Sort historical data by timestamp
        sorted_history = sorted(
            historical_data,
            key=lambda x: datetime.fromisoformat(x["assessment_date"])
        )
        
        # Extract historical risk scores
        timestamps = [datetime.fromisoformat(x["assessment_date"]) for x in sorted_history]
        risk_scores = [x["overall_risk"] for x in sorted_history]
        
        # Calculate time differences in days and convert to relative positions
        if len(timestamps) <= 1:
            # Cannot calculate time differences with only one point
            time_positions = [0]
        else:
            # Convert to relative positions (first point is 0)
            start_time = timestamps[0]
            time_positions = [(t - start_time).days for t in timestamps]
        
        # Use linear regression for forecasting
        forecast_result = self._linear_regression_forecast(
            time_positions, risk_scores, forecast_periods, period_months
        )
        
        # If age is a dominant factor, adjust the forecast to account for
        # non-linear aging effects
        age_adjusted_forecast = self._adjust_for_age_factor(
            equipment, forecast_result["forecasted_values"]
        )
        
        # Detect if any forecasted values exceed critical threshold
        critical_threshold = 85
        exceeds_critical = any(score >= critical_threshold for score in age_adjusted_forecast)
        
        # Identify when equipment will reach critical risk (if at all)
        time_to_critical = None
        if not exceeds_critical:
            # Check if trend suggests it will reach critical
            if forecast_result["trend_slope"] > 0:
                # Calculate months until critical based on current risk and slope
                current_risk = risk_scores[-1]
                if current_risk < critical_threshold:
                    risk_increase_needed = critical_threshold - current_risk
                    months_needed = risk_increase_needed / forecast_result["trend_slope"]
                    time_to_critical = math.ceil(months_needed)
        else:
            # Find first month that exceeds critical
            for i, score in enumerate(age_adjusted_forecast):
                if score >= critical_threshold:
                    time_to_critical = (i + 1) * period_months
                    break
        
        # Generate forecast periods (dates)
        last_date = timestamps[-1]
        forecast_dates = [
            (last_date + timedelta(days=30 * period_months * (i + 1))).strftime("%Y-%m")
            for i in range(forecast_periods)
        ]
        
        return {
            "equipment_id": equipment.id,
            "data_points_used": len(historical_data),
            "current_risk": risk_scores[-1],
            "forecast_periods": forecast_dates,
            "forecasted_values": [round(x, 1) for x in age_adjusted_forecast],
            "trend": forecast_result["trend"],
            "confidence": forecast_result["confidence"],
            "time_to_critical": time_to_critical,
            "exceeds_critical_in_forecast": exceeds_critical,
            "forecast_date": datetime.now().isoformat()
        }
    
    def forecast_facility_risk(self, facility: Facility,
                              historical_data: List[Dict[str, Any]],
                              equipment_forecasts: Optional[List[Dict[str, Any]]] = None,
                              forecast_periods: int = 6,
                              period_months: int = 1) -> Dict[str, Any]:
        """
        Forecast future risk for a facility based on historical data.
        
        Args:
            facility: Facility to forecast
            historical_data: List of historical facility risk assessments
            equipment_forecasts: Optional list of equipment forecasts within facility
            forecast_periods: Number of periods to forecast
            period_months: Number of months per period
            
        Returns:
            Dictionary with forecast results
        """
        if not historical_data or len(historical_data) < 3:
            return {
                "facility_id": facility.id,
                "error": "Insufficient historical data for forecasting",
                "minimum_history_required": 3,
                "history_available": len(historical_data) if historical_data else 0
            }
        
        # Sort historical data by timestamp
        sorted_history = sorted(
            historical_data,
            key=lambda x: datetime.fromisoformat(x["calculated_at"])
        )
        
        # Extract historical risk scores
        timestamps = [datetime.fromisoformat(x["calculated_at"]) for x in sorted_history]
        risk_scores = [x["overall_risk_score"] for x in sorted_history]
        
        # Calculate time differences in days and convert to relative positions
        if len(timestamps) <= 1:
            # Cannot calculate time differences with only one point
            time_positions = [0]
        else:
            # Convert to relative positions (first point is 0)
            start_time = timestamps[0]
            time_positions = [(t - start_time).days for t in timestamps]
        
        # Use linear regression for forecasting
        facility_forecast = self._linear_regression_forecast(
            time_positions, risk_scores, forecast_periods, period_months
        )
        
        # Generate forecast periods (dates)
        last_date = timestamps[-1]
        forecast_dates = [
            (last_date + timedelta(days=30 * period_months * (i + 1))).strftime("%Y-%m")
            for i in range(forecast_periods)
        ]
        
        # If we have equipment forecasts, use them to adjust facility forecast
        blended_forecast = facility_forecast["forecasted_values"]
        
        if equipment_forecasts and len(equipment_forecasts) > 0:
            # Count equipment with worsening forecasts
            worsening_count = sum(
                1 for ef in equipment_forecasts if ef["trend"] == "worsening"
            )
            
            # If significant number of equipment forecasts show worsening trend,
            # adjust the facility forecast to account for this
            if worsening_count > len(equipment_forecasts) / 3:  # More than 1/3
                # Blend facility forecast with equipment forecast trends
                blended_forecast = self._blend_with_equipment_forecasts(
                    facility_forecast["forecasted_values"],
                    equipment_forecasts,
                    blend_factor=0.3  # 30% influence from equipment forecasts
                )
        
        # Detect if any forecasted values exceed critical threshold
        critical_threshold = 85
        exceeds_critical = any(score >= critical_threshold for score in blended_forecast)
        
        # Identify when facility will reach critical risk (if at all)
        time_to_critical = None
        if not exceeds_critical:
            # Check if trend suggests it will reach critical
            if facility_forecast["trend_slope"] > 0:
                # Calculate months until critical based on current risk and slope
                current_risk = risk_scores[-1]
                if current_risk < critical_threshold:
                    risk_increase_needed = critical_threshold - current_risk
                    months_needed = risk_increase_needed / facility_forecast["trend_slope"]
                    time_to_critical = math.ceil(months_needed)
        else:
            # Find first month that exceeds critical
            for i, score in enumerate(blended_forecast):
                if score >= critical_threshold:
                    time_to_critical = (i + 1) * period_months
                    break
        
        return {
            "facility_id": facility.id,
            "data_points_used": len(historical_data),
            "current_risk": risk_scores[-1],
            "forecast_periods": forecast_dates,
            "forecasted_values": [round(x, 1) for x in blended_forecast],
            "trend": facility_forecast["trend"],
            "confidence": facility_forecast["confidence"],
            "time_to_critical": time_to_critical,
            "exceeds_critical_in_forecast": exceeds_critical,
            "equipment_worsening_count": worsening_count if equipment_forecasts else None,
            "equipment_count": len(equipment_forecasts) if equipment_forecasts else None,
            "forecast_date": datetime.now().isoformat()
        }
    
    def forecast_maintenance_needs(self, equipment: Equipment,
                                  historical_data: List[Dict[str, Any]],
                                  risk_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forecast future maintenance needs based on risk forecast and history.
        
        Args:
            equipment: Equipment to forecast maintenance for
            historical_data: List of historical risk assessments
            risk_forecast: Risk forecast data for this equipment
            
        Returns:
            Dictionary with maintenance forecast
        """
        # Start with basic response structure
        response = {
            "equipment_id": equipment.id,
            "equipment_type": equipment.type.value,
            "current_date": datetime.now().isoformat(),
        }
        
        # Check if we have sufficient data
        if not historical_data or "error" in risk_forecast:
            response["error"] = "Insufficient data for maintenance forecasting"
            return response
        
        # Extract risk trend
        risk_trend = risk_forecast["trend"]
        forecast_values = risk_forecast["forecasted_values"]
        
        # Calculate maintenance urgency based on risk forecast
        if risk_trend == "worsening" and max(forecast_values) > 70:
            # High risk equipment with worsening trend
            urgency = "urgent"
            recommended_timeframe = "Within 1 month"
        elif risk_trend == "worsening" and max(forecast_values) > 50:
            # Medium risk equipment with worsening trend
            urgency = "high"
            recommended_timeframe = "Within 3 months"
        elif max(forecast_values) > 70:
            # High risk equipment with stable trend
            urgency = "medium"
            recommended_timeframe = "Within 6 months"
        elif risk_trend == "worsening":
            # Any equipment with worsening trend
            urgency = "medium"
            recommended_timeframe = "Within 6 months"
        else:
            # Low or stable risk
            urgency = "normal"
            recommended_timeframe = "Regular schedule"
        
        # Recommend specific maintenance types based on equipment type and risk
        maintenance_types = self._get_recommended_maintenance(equipment, forecast_values)
        
        # Return maintenance forecast
        response.update({
            "maintenance_urgency": urgency,
            "recommended_timeframe": recommended_timeframe,
            "recommended_maintenance": maintenance_types,
            "risk_trajectory": risk_trend,
            "max_forecasted_risk": max(forecast_values)
        })
        
        return response
    
    def _linear_regression_forecast(self, time_positions: List[int],
                                   values: List[float],
                                   forecast_periods: int,
                                   period_months: int) -> Dict[str, Any]:
        """
        Use linear regression to forecast future values.
        
        Args:
            time_positions: List of time positions (in days from start)
            values: List of historical values
            forecast_periods: Number of periods to forecast
            period_months: Number of months per period
            
        Returns:
            Dictionary with forecast results
        """
        # Convert lists to numpy arrays
        x = np.array(time_positions)
        y = np.array(values)
        
        # Add constant term for intercept
        X = np.vstack([x, np.ones(len(x))]).T
        
        # Perform linear regression
        # y = ax + b
        a, b = np.linalg.lstsq(X, y, rcond=None)[0]
        
        # Calculate R-squared to assess goodness of fit
        y_pred = a * x + b
        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)
        r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
        
        # Generate forecast
        last_time = time_positions[-1] if time_positions else 0
        forecast_times = [
            last_time + (30 * period_months * (i + 1))  # Convert months to days
            for i in range(forecast_periods)
        ]
        forecasted_values = [a * t + b for t in forecast_times]
        
        # Cap forecasted values between 0 and 100
        forecasted_values = [max(0, min(100, val)) for val in forecasted_values]
        
        # Determine trend direction
        if abs(a) < 0.1:  # Very small slope
            trend = "stable"
        else:
            trend = "worsening" if a > 0 else "improving"
        
        # Determine confidence level based on R-squared
        if r_squared > 0.7:
            confidence = "high"
        elif r_squared > 0.4:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "forecasted_values": forecasted_values,
            "trend": trend,
            "confidence": confidence,
            "r_squared": r_squared,
            "trend_slope": a,
            "intercept": b
        }
    
    def _adjust_for_age_factor(self, equipment: Equipment, 
                              forecasted_values: List[float]) -> List[float]:
        """
        Adjust forecast values to account for non-linear aging effects.
        
        Args:
            equipment: Equipment being forecasted
            forecasted_values: Linear forecasted values
            
        Returns:
            Adjusted forecast values
        """
        # Get equipment age in years
        age_delta = datetime.now() - equipment.installation_date
        current_age_years = age_delta.days / 365.25
        
        # Typical service life by equipment type
        service_life_map = {
            "PANEL": 35,
            "TRANSFORMER": 25,
            "SWITCHGEAR": 30,
            "BREAKER": 20,
            "OTHER": 20
        }
        
        # Get expected service life for this equipment type
        expected_life = service_life_map.get(equipment.type.value, 20)
        
        # Calculate life percentage
        life_percentage = (current_age_years / expected_life) * 100
        
        # Adjust forecast based on current life percentage
        adjusted_values = []
        for i, value in enumerate(forecasted_values):
            # Each forecast period advances age by period_months (default 1 month)
            # Convert to years for calculation
            additional_age_years = (i + 1) / 12
            future_age_years = current_age_years + additional_age_years
            future_life_percentage = (future_age_years / expected_life) * 100
            
            # Apply non-linear adjustment based on equipment age curve
            # Equipment in the last 20% of life ages more rapidly
            if future_life_percentage > 80:
                # Accelerated aging in last 20% of life
                acceleration_factor = 1.0 + ((future_life_percentage - 80) / 20) * 0.5
                adjusted_value = value * acceleration_factor
            else:
                adjusted_value = value
            
            # Ensure adjusted value doesn't exceed 100
            adjusted_values.append(min(100, adjusted_value))
        
        return adjusted_values
    
    def _blend_with_equipment_forecasts(self, 
                                       facility_forecast: List[float],
                                       equipment_forecasts: List[Dict[str, Any]],
                                       blend_factor: float = 0.3) -> List[float]:
        """
        Blend facility forecast with equipment forecasts.
        
        Args:
            facility_forecast: Forecasted values for facility
            equipment_forecasts: List of equipment forecasts
            blend_factor: How much to weigh equipment forecasts (0-1)
            
        Returns:
            Blended forecast values
        """
        # Check if we have the same number of forecast periods for all
        forecast_periods = len(facility_forecast)
        
        # Create aggregate equipment forecast by averaging
        # Only include forecasts with the same number of periods
        valid_equipment_forecasts = [
            ef for ef in equipment_forecasts 
            if "forecasted_values" in ef and len(ef["forecasted_values"]) == forecast_periods
        ]
        
        if not valid_equipment_forecasts:
            return facility_forecast
        
        # Calculate average equipment forecast for each period
        avg_equipment_forecast = []
        for period in range(forecast_periods):
            period_values = [ef["forecasted_values"][period] for ef in valid_equipment_forecasts]
            avg_equipment_forecast.append(sum(period_values) / len(period_values))
        
        # Blend facility and equipment forecasts
        blended_forecast = [
            (1 - blend_factor) * facility_forecast[i] + blend_factor * avg_equipment_forecast[i]
            for i in range(forecast_periods)
        ]
        
        return blended_forecast
    
    def _get_recommended_maintenance(self, equipment: Equipment, 
                                    forecast_values: List[float]) -> List[Dict[str, Any]]:
        """
        Get recommended maintenance types based on equipment and forecast.
        
        Args:
            equipment: Equipment to recommend maintenance for
            forecast_values: Forecasted risk values
            
        Returns:
            List of recommended maintenance types with details
        """
        maintenance_recommendations = []
        
        # Default recommendation for all equipment
        maintenance_recommendations.append({
            "type": "visual_inspection",
            "description": "Complete visual inspection",
            "priority": "high" if max(forecast_values) > 70 else "medium"
        })
        
        # Add thermographic scanning for all equipment
        maintenance_recommendations.append({
            "type": "thermographic",
            "description": "Infrared thermographic scanning",
            "priority": "high" if max(forecast_values) > 70 else "medium"
        })
        
        # Add specific maintenance based on equipment type
        if equipment.type.value == "PANEL":
            maintenance_recommendations.append({
                "type": "connection_tightness",
                "description": "Check and tighten all connections",
                "priority": "high" if max(forecast_values) > 60 else "medium"
            })
            
        elif equipment.type.value == "TRANSFORMER":
            maintenance_recommendations.append({
                "type": "oil_analysis",
                "description": "Transformer oil analysis",
                "priority": "high"
            })
            maintenance_recommendations.append({
                "type": "insulation_test",
                "description": "Insulation resistance testing",
                "priority": "high" if max(forecast_values) > 60 else "medium"
            })
            
        elif equipment.type.value == "SWITCHGEAR":
            maintenance_recommendations.append({
                "type": "mechanism_test",
                "description": "Test operating mechanism",
                "priority": "high"
            })
            maintenance_recommendations.append({
                "type": "connection_tightness",
                "description": "Check and tighten all connections",
                "priority": "high"
            })
            
        elif equipment.type.value == "BREAKER":
            maintenance_recommendations.append({
                "type": "trip_test",
                "description": "Conduct breaker trip testing",
                "priority": "high"
            })
            maintenance_recommendations.append({
                "type": "mechanism_test",
                "description": "Test operating mechanism",
                "priority": "medium"
            })
        
        # Add recommendation if equipment is heavily loaded
        if equipment.loading_percentage > 80:
            maintenance_recommendations.append({
                "type": "load_distribution",
                "description": "Evaluate load distribution and capacity",
                "priority": "high"
            })
        
        return maintenance_recommendations 