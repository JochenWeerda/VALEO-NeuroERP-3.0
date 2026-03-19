"""
Optimization solver service for rations optimization
"""
from typing import List, Dict, Any
from ..schemas.feed import FeedIngredient
from ..schemas.requirement import NutrientRequirements
from ..schemas.optimization import OptimizationOptions, OptimizationResult
from .ration_model import RationOptimizationModel
from ..domain.enums import OptimizationStatus
import logging

logger = logging.getLogger(__name__)

class OptimizationService:
    """Service for solving ration optimization problems"""
    
    def __init__(self):
        self.model = RationOptimizationModel()
    
    def optimize_ration(
        self, 
        feeds: List[FeedIngredient], 
        requirements: NutrientRequirements, 
        options: OptimizationOptions
    ) -> OptimizationResult:
        """
        Solve the ration optimization problem
        
        Args:
            feeds: Available feed ingredients
            requirements: Nutrient requirements
            options: Optimization options
            
        Returns:
            OptimizationResult with the solution
        """
        logger.info("Starting ration optimization")
        
        # Build the optimization model
        self.model.build_model(feeds, requirements, options)
        
        # Solve the model
        status, solution_data = self.model.solve()
        
        # Build the solution objects
        if status == OptimizationStatus.OPTIMAL:
            ration_items, nutrient_supply, constraint_report, warnings = self.model.build_solution(solution_data)
            total_cost = solution_data["objective_value"] or 0.0
        else:
            # For non-optimal solutions, create empty results
            ration_items = []
            nutrient_supply = self.model._create_empty_nutrient_supply()
            constraint_report = []
            warnings = [f"Optimization failed with status: {status.value}"]
            total_cost = 0.0
            
            # Still try to build constraint report for debugging
            if solution_data.get("variable_values"):
                constraint_report = self.model._build_constraint_report(solution_data["variable_values"])
        
        # Create the result
        result = OptimizationResult(
            status=status.value,
            objective_value=solution_data["objective_value"],
            total_cost_eur_day=total_cost,
            ration_items=ration_items,
            nutrient_supply=nutrient_supply,
            constraint_report=constraint_report,
            warnings=warnings,
            metadata={
                "solver": options.solver_name,
                "solve_time_sec": solution_data.get("solve_time"),
                "iterations": solution_data.get("iterations"),
                "num_feeds": len(feeds),
                "num_constraints": len(self.model.model.constraints) if self.model.model else 0
            }
        )
        
        logger.info(f"Optimization completed with status: {status.value}")
        return result
    
    def validate_feeds(self, feeds: List[FeedIngredient]) -> List[str]:
        """
        Validate feed ingredients for consistency and correctness
        
        Args:
            feeds: List of feed ingredients to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check for duplicate IDs
        ids = [feed.id for feed in feeds]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in ids if ids.count(id) > 1]
            errors.append(f"Duplicate feed IDs found: {list(set(duplicates))}")
        
        # Check for duplicate names
        names = [feed.name for feed in feeds]
        if len(names) != len(set(names)):
            duplicates = [name for name in names if names.count(name) > 1]
            errors.append(f"Duplicate feed names found: {list(set(duplicates))}")
        
        # Validate each feed
        for feed in feeds:
            # Check DM fraction
            if feed.dm_frac <= 0 or feed.dm_frac > 1:
                errors.append(f"Feed '{feed.name}': dm_frac must be between 0 and 1 (exclusive of 0)")
            
            # Check bounds
            if feed.min_kgdm < 0:
                errors.append(f"Feed '{feed.name}': min_kgdm cannot be negative")
            
            if feed.max_kgdm < feed.min_kgdm:
                errors.append(f"Feed '{feed.name}': max_kgdm must be >= min_kgdm")
            
            # Check for negative nutrient values
            nutrient_fields = [
                ('me_mj_kgdm', 'ME'),
                ('sidp_g_kgdm', 'SIDP'),
                ('andfom_g_kgdm', 'aNDFom'),
                ('starch_g_kgdm', 'Starch'),
                ('sugar_g_kgdm', 'Sugar'),
                ('fat_g_kgdm', 'Fat'),
                ('ca_g_kgdm', 'Calcium'),
                ('p_g_kgdm', 'Phosphorus'),
                ('na_g_kgdm', 'Sodium')
            ]
            
            for field, name in nutrient_fields:
                value = getattr(feed, field)
                if value < 0:
                    errors.append(f"Feed '{feed.name}': {name} cannot be negative")
            
            # Check price
            if feed.price_eur_kgdm < 0:
                errors.append(f"Feed '{feed.name}': price cannot be negative")
        
        return errors