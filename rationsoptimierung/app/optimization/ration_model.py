"""
Ration optimization model using PuLP for linear programming
"""
import pulp
from typing import List, Dict, Any, Tuple
from ..schemas.feed import FeedIngredient
from ..schemas.requirement import NutrientRequirements
from ..schemas.optimization import OptimizationOptions, RationItem, NutrientSupply, ConstraintReportItem
from ..domain.enums import OptimizationStatus, ConstraintStatus, SolverName
import logging

logger = logging.getLogger(__name__)

class RationOptimizationModel:
    """Linear optimization model for dairy cow rations"""
    
    def __init__(self):
        self.model = None
        self.decision_vars = {}
        self.feeds = []
        self.requirements = None
        self.options = None
        
    def build_model(
        self, 
        feeds: List[FeedIngredient], 
        requirements: NutrientRequirements, 
        options: OptimizationOptions
    ) -> None:
        """
        Build the linear optimization model
        
        Args:
            feeds: List of available feed ingredients
            requirements: Nutrient requirements for the cow
            options: Optimization options
        """
        self.feeds = feeds
        self.requirements = requirements
        self.options = options
        
        # Create the optimization problem
        self.model = pulp.LpProblem("DairyCowRationOptimization", pulp.LpMinimize)
        
        # Create decision variables (kg DM of each feed per cow per day)
        self.decision_vars = {}
        for feed in feeds:
            self.decision_vars[feed.id] = pulp.LpVariable(
                f"x_{feed.id}",
                lowBound=feed.min_kgdm,
                upBound=feed.max_kgdm,
                cat='Continuous'
            )
        
        # Objective function: minimize total cost
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.price_eur_kgdm 
            for feed in feeds
        ]), "Total_Cost"
        
        # Constraint 1: Dry matter intake equality
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] for feed in feeds
        ]) == requirements.dmi_kg, "DMI_Equality"
        
        # Constraint 2: Minimum metabolizable energy
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.me_mj_kgdm for feed in feeds
        ]) >= requirements.me_min_mj, "ME_Minimum"
        
        # Constraint 3: Minimum small intestine digestible protein
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.sidp_g_kgdm for feed in feeds
        ]) >= requirements.sidp_min_g, "SIDP_Minimum"
        
        # Constraint 4: Minimum aNDFom
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.andfom_g_kgdm for feed in feeds
        ]) >= requirements.andfom_min_g, "aNDFom_Minimum"
        
        # Constraint 5: Maximum aNDFom
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.andfom_g_kgdm for feed in feeds
        ]) <= requirements.andfom_max_g, "aNDFom_Maximum"
        
        # Constraint 6: Maximum starch
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.starch_g_kgdm for feed in feeds
        ]) <= requirements.starch_max_g, "Starch_Maximum"
        
        # Constraint 7: Maximum sugar
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.sugar_g_kgdm for feed in feeds
        ]) <= requirements.sugar_max_g, "Sugar_Maximum"
        
        # Constraint 8: Maximum fat
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.fat_g_kgdm for feed in feeds
        ]) <= requirements.fat_max_g, "Fat_Maximum"
        
        # Constraint 9: Minimum calcium
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.ca_g_kgdm for feed in feeds
        ]) >= requirements.ca_min_g, "Ca_Minimum"
        
        # Constraint 10: Minimum phosphorus
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.p_g_kgdm for feed in feeds
        ]) >= requirements.p_min_g, "P_Minimum"
        
        # Constraint 11: Minimum sodium
        self.model += pulp.lpSum([
            self.decision_vars[feed.id] * feed.na_g_kgdm for feed in feeds
        ]) >= requirements.na_min_g, "Na_Minimum"
        
        # Constraint 12: Minimum forage share
        forage_feeds = [f for f in feeds if f.group.value == "forage"]
        if forage_feeds:
            self.model += pulp.lpSum([
                self.decision_vars[feed.id] for feed in forage_feeds
            ]) >= requirements.forage_share_min * requirements.dmi_kg, "Forage_Share_Minimum"
        
        logger.info(f"Built optimization model with {len(feeds)} feeds and {len(self.model.constraints)} constraints")
    
    def solve(self) -> Tuple[OptimizationStatus, Dict[str, Any]]:
        """
        Solve the optimization model
        
        Returns:
            Tuple of (status, solution_data)
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Select solver
        solver_name = self.options.solver_name
        if solver_name == SolverName.CBC:
            solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=self.options.max_solver_time_sec)
        elif solver_name == SolverName.GLPK:
            solver = pulp.GLPK_CMD(msg=False, timeLimit=self.options.max_solver_time_sec)
        else:
            # Default to CBC
            solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=self.options.max_solver_time_sec)
        
        # Solve the model
        self.model.solve(solver)
        
        # Determine status
        status_map = {
            pulp.LpStatusOptimal: OptimizationStatus.OPTIMAL,
            pulp.LpStatusInfeasible: OptimizationStatus.INFEASIBLE,
            pulp.LpStatusUnbounded: OptimizationStatus.UNBOUNDED,
            pulp.LpStatusUndefined: OptimizationStatus.UNKNOWN
        }
        
        status = status_map.get(self.model.status, OptimizationStatus.UNKNOWN)
        
        # Prepare solution data
        solution_data = {
            "status": status,
            "objective_value": pulp.value(self.model.objective) if self.model.status == pulp.LpStatusOptimal else None,
            "variable_values": {
                var.name: var.varValue for var in self.model.variables()
            } if self.model.status == pulp.LpStatusOptimal else {},
            "constraint_values": {
                name: constraint.value() for name, constraint in self.model.constraints.items()
            } if self.model.status == pulp.LpStatusOptimal else {},
            "solve_time": None,  # PuLP doesn't provide this easily
            "iterations": None   # PuLP doesn't provide this easily
        }
        
        logger.info(f"Optimization completed with status: {status}")
        return status, solution_data
    
    def build_solution(
        self, 
        solution_data: Dict[str, Any]
    ) -> Tuple[
        List[RationItem], 
        NutrientSupply, 
        List[ConstraintReportItem], 
        List[str]
    ]:
        """
        Build the solution objects from solver results
        
        Args:
            solution_data: Data returned from solve()
            
        Returns:
            Tuple of (ration_items, nutrient_supply, constraint_report, warnings)
        """
        if solution_data["status"] != OptimizationStatus.OPTIMAL:
            # Return empty solution for non-optimal status
            return [], self._create_empty_nutrient_supply(), [], ["Optimization did not reach optimal solution"]
        
        variable_values = solution_data["variable_values"]
        
        # Build ration items
        ration_items = []
        total_cost = 0.0
        
        for feed in self.feeds:
            var_name = f"x_{feed.id}"
            kgdm = variable_values.get(var_name, 0.0)
            
            if kgdm > 0.001:  # Only include feeds with meaningful amounts
                # Calculate fresh matter (kg FM = kg DM / DM fraction)
                kgfm = kgdm / feed.dm_frac if feed.dm_frac > 0 else 0.0
                unit_cost = feed.price_eur_kgdm
                total_cost_for_feed = kgdm * unit_cost
                
                ration_items.append(RationItem(
                    feed_id=feed.id,
                    name=feed.name,
                    kgdm=kgdm,
                    kgfm=kgfm,
                    unit_cost=unit_cost,
                    total_cost=total_cost_for_feed
                ))
                
                total_cost += total_cost_for_feed
        
        # Build nutrient supply
        nutrient_supply = self._calculate_nutrient_supply(variable_values)
        
        # Build constraint report
        constraint_report = self._build_constraint_report(variable_values)
        
        # Generate warnings
        warnings = self._generate_warnings(variable_values)
        
        return ration_items, nutrient_supply, constraint_report, warnings
    
    def _calculate_nutrient_supply(self, variable_values: Dict[str, float]) -> NutrientSupply:
        """Calculate nutrient supply from solution"""
        totals = {
            "dmi_kg": 0.0,
            "me_mj": 0.0,
            "sidp_g": 0.0,
            "andfom_g": 0.0,
            "starch_g": 0.0,
            "sugar_g": 0.0,
            "fat_g": 0.0,
            "ca_g": 0.0,
            "p_g": 0.0,
            "na_g": 0.0
        }
        
        forage_dmi = 0.0
        
        for feed in self.feeds:
            var_name = f"x_{feed.id}"
            kgdm = variable_values.get(var_name, 0.0)
            
            if kgdm > 0:
                totals["dmi_kg"] += kgdm
                totals["me_mj"] += kgdm * feed.me_mj_kgdm
                totals["sidp_g"] += kgdm * feed.sidp_g_kgdm
                totals["andfom_g"] += kgdm * feed.andfom_g_kgdm
                totals["starch_g"] += kgdm * feed.starch_g_kgdm
                totals["sugar_g"] += kgdm * feed.sugar_g_kgdm
                totals["fat_g"] += kgdm * feed.fat_g_kgdm
                totals["ca_g"] += kgdm * feed.ca_g_kgdm
                totals["p_g"] += kgdm * feed.p_g_kgdm
                totals["na_g"] += kgdm * feed.na_g_kgdm
                
                if feed.group.value == "forage":
                    forage_dmi += kgdm
        
        # Calculate forage share percentage
        forage_share_pct = (forage_dmi / totals["dmi_kg"] * 100) if totals["dmi_kg"] > 0 else 0.0
        
        return NutrientSupply(
            dmi_kg=totals["dmi_kg"],
            me_mj=totals["me_mj"],
            sidp_g=totals["sidp_g"],
            andfom_g=totals["andfom_g"],
            starch_g=totals["starch_g"],
            sugar_g=totals["sugar_g"],
            fat_g=totals["fat_g"],
            ca_g=totals["ca_g"],
            p_g=totals["p_g"],
            na_g=totals["na_g"],
            forage_share_pct=forage_share_pct
        )
    
    def _build_constraint_report(self, variable_values: Dict[str, float]) -> List[ConstraintReportItem]:
        """Build constraint fulfillment report"""
        report = []
        
        # DMI constraint
        actual_dmi = sum(variable_values.get(f"x_{feed.id}", 0.0) for feed in self.feeds)
        report.append(ConstraintReportItem(
            name="Dry Matter Intake",
            target=self.requirements.dmi_kg,
            actual=actual_dmi,
            difference=actual_dmi - self.requirements.dmi_kg,
            fulfilled=abs(actual_dmi - self.requirements.dmi_kg) < 0.001,
            status="OK" if abs(actual_dmi - self.requirements.dmi_kg) < 0.001 else "NOT_MET"
        ))
        
        # ME constraint
        actual_me = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.me_mj_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Metabolizable Energy",
            target=self.requirements.me_min_mj,
            actual=actual_me,
            difference=actual_me - self.requirements.me_min_mj,
            fulfilled=actual_me >= self.requirements.me_min_mj - 0.001,
            status="OK" if actual_me >= self.requirements.me_min_mj - 0.001 else "MIN_NOT_MET"
        ))
        
        # SIDP constraint
        actual_sidp = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.sidp_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Small Intestine Digestible Protein",
            target=self.requirements.sidp_min_g,
            actual=actual_sidp,
            difference=actual_sidp - self.requirements.sidp_min_g,
            fulfilled=actual_sidp >= self.requirements.sidp_min_g - 0.001,
            status="OK" if actual_sidp >= self.requirements.sidp_min_g - 0.001 else "MIN_NOT_MET"
        ))
        
        # aNDFom minimum constraint
        actual_andfom_min = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.andfom_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="aNDFom Minimum",
            target=self.requirements.andfom_min_g,
            actual=actual_andfom_min,
            difference=actual_andfom_min - self.requirements.andfom_min_g,
            fulfilled=actual_andfom_min >= self.requirements.andfom_min_g - 0.001,
            status="OK" if actual_andfom_min >= self.requirements.andfom_min_g - 0.001 else "MIN_NOT_MET"
        ))
        
        # aNDFom maximum constraint
        actual_andfom_max = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.andfom_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="aNDFom Maximum",
            target=self.requirements.andfom_max_g,
            actual=actual_andfom_max,
            difference=actual_andfom_max - self.requirements.andfom_max_g,
            fulfilled=actual_andfom_max <= self.requirements.andfom_max_g + 0.001,
            status="OK" if actual_andfom_max <= self.requirements.andfom_max_g + 0.001 else "MAX_EXCEEDED"
        ))
        
        # Starch constraint
        actual_starch = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.starch_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Starch Maximum",
            target=self.requirements.starch_max_g,
            actual=actual_starch,
            difference=actual_starch - self.requirements.starch_max_g,
            fulfilled=actual_starch <= self.requirements.starch_max_g + 0.001,
            status="OK" if actual_starch <= self.requirements.starch_max_g + 0.001 else "MAX_EXCEEDED"
        ))
        
        # Sugar constraint
        actual_sugar = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.sugar_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Sugar Maximum",
            target=self.requirements.sugar_max_g,
            actual=actual_sugar,
            difference=actual_sugar - self.requirements.sugar_max_g,
            fulfilled=actual_sugar <= self.requirements.sugar_max_g + 0.001,
            status="OK" if actual_sugar <= self.requirements.sugar_max_g + 0.001 else "MAX_EXCEEDED"
        ))
        
        # Fat constraint
        actual_fat = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.fat_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Fat Maximum",
            target=self.requirements.fat_max_g,
            actual=actual_fat,
            difference=actual_fat - self.requirements.fat_max_g,
            fulfilled=actual_fat <= self.requirements.fat_max_g + 0.001,
            status="OK" if actual_fat <= self.requirements.fat_max_g + 0.001 else "MAX_EXCEEDED"
        ))
        
        # Calcium constraint
        actual_ca = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.ca_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Calcium Minimum",
            target=self.requirements.ca_min_g,
            actual=actual_ca,
            difference=actual_ca - self.requirements.ca_min_g,
            fulfilled=actual_ca >= self.requirements.ca_min_g - 0.001,
            status="OK" if actual_ca >= self.requirements.ca_min_g - 0.001 else "MIN_NOT_MET"
        ))
        
        # Phosphorus constraint
        actual_p = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.p_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Phosphorus Minimum",
            target=self.requirements.p_min_g,
            actual=actual_p,
            difference=actual_p - self.requirements.p_min_g,
            fulfilled=actual_p >= self.requirements.p_min_g - 0.001,
            status="OK" if actual_p >= self.requirements.p_min_g - 0.001 else "MIN_NOT_MET"
        ))
        
        # Sodium constraint
        actual_na = sum(
            variable_values.get(f"x_{feed.id}", 0.0) * feed.na_g_kgdm 
            for feed in self.feeds
        )
        report.append(ConstraintReportItem(
            name="Sodium Minimum",
            target=self.requirements.na_min_g,
            actual=actual_na,
            difference=actual_na - self.requirements.na_min_g,
            fulfilled=actual_na >= self.requirements.na_min_g - 0.001,
            status="OK" if actual_na >= self.requirements.na_min_g - 0.001 else "MIN_NOT_MET"
        ))
        
        # Forage share constraint
        forage_feeds = [f for f in self.feeds if f.group.value == "forage"]
        if forage_feeds:
            actual_forage_dmi = sum(
                variable_values.get(f"x_{feed.id}", 0.0) 
                for feed in forage_feeds
            )
            target_forage = self.requirements.forage_share_min * self.requirements.dmi_kg
            report.append(ConstraintReportItem(
                name="Forage Share Minimum",
                target=target_forage,
                actual=actual_forage_dmi,
                difference=actual_forage_dmi - target_forage,
                fulfilled=actual_forage_dmi >= target_forage - 0.001,
                status="OK" if actual_forage_dmi >= target_forage - 0.001 else "MIN_NOT_MET"
            ))
        
        # Individual feed bounds
        for feed in self.feeds:
            var_name = f"x_{feed.id}"
            actual_amount = variable_values.get(var_name, 0.0)
            
            # Minimum bound
            report.append(ConstraintReportItem(
                name=f"{feed.name} Minimum Bound",
                target=feed.min_kgdm,
                actual=actual_amount,
                difference=actual_amount - feed.min_kgdm,
                fulfilled=actual_amount >= feed.min_kgdm - 0.001,
                status="OK" if actual_amount >= feed.min_kgdm - 0.001 else "MIN_NOT_MET"
            ))
            
            # Maximum bound
            report.append(ConstraintReportItem(
                name=f"{feed.name} Maximum Bound",
                target=feed.max_kgdm,
                actual=actual_amount,
                difference=actual_amount - feed.max_kgdm,
                fulfilled=actual_amount <= feed.max_kgdm + 0.001,
                status="OK" if actual_amount <= feed.max_kgdm + 0.001 else "MAX_EXCEEDED"
            ))
        
        return report
    
    def _generate_warnings(self, variable_values: Dict[str, float]) -> List[str]:
        """Generate warnings about the solution"""
        warnings = []
        
        # Check for high concentration on single feeds
        total_dmi = sum(variable_values.values())
        if total_dmi > 0:
            for feed in self.feeds:
                var_name = f"x_{feed.id}"
                amount = variable_values.get(var_name, 0.0)
                proportion = amount / total_dmi if total_dmi > 0 else 0
                
                if proportion > 0.8:  # More than 80% from single feed
                    warnings.append(
                        f"High concentration detected: {feed.name} provides {proportion*100:.1f}% of DMI"
                    )
        
        # Check for feeds at bounds
        for feed in self.feeds:
            var_name = f"x_{feed.id}"
            amount = variable_values.get(var_name, 0.0)
            
            if abs(amount - feed.min_kgdm) < 0.01:
                warnings.append(f"Feed {feed.name} is at its minimum bound ({feed.min_kgdm} kg DM)")
            elif abs(amount - feed.max_kgdm) < 0.01:
                warnings.append(f"Feed {feed.name} is at its maximum bound ({feed.max_kgdm} kg DM)")
        
        # Check for missing mineral feeds if calcium/phosphorus/sodium are high
        mineral_feeds = [f for f in self.feeds if f.group.value == "mineral"]
        total_mineral_dmi = sum(
            variable_values.get(f"x_{feed.id}", 0.0) 
            for feed in mineral_feeds
        )
        
        if total_mineral_dmi < 0.1 and (
            self.requirements.ca_min_g > 50 or 
            self.requirements.p_min_g > 30 or 
            self.requirements.na_min_g > 5
        ):
            warnings.append(
                "Low mineral feed usage detected. Consider adding mineral sources to meet Ca, P, Na requirements."
            )
        
        return warnings
    
    def _create_empty_nutrient_supply(self) -> NutrientSupply:
        """Create an empty nutrient supply for infeasible solutions"""
        return NutrientSupply(
            dmi_kg=0.0,
            me_mj=0.0,
            sidp_g=0.0,
            andfom_g=0.0,
            starch_g=0.0,
            sugar_g=0.0,
            fat_g=0.0,
            ca_g=0.0,
            p_g=0.0,
            na_g=0.0,
            forage_share_pct=0.0
        )