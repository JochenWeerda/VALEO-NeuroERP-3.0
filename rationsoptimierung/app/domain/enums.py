from enum import Enum

class FeedGroup(str, Enum):
    """Classification of feed ingredients"""
    FORAGE = "forage"
    CONCENTRATE = "concentrate"
    PROTEIN = "protein"
    MINERAL = "mineral"
    OTHER = "other"

class OptimizationStatus(str, Enum):
    """Status of optimization solution"""
    OPTIMAL = "optimal"
    INFEASIBLE = "infeasible"
    UNBOUNDED = "unbounded"
    TIME_LIMIT = "time_limit"
    ITERATION_LIMIT = "iteration_limit"
    NUMERICAL_ERROR = "numerical_error"
    UNKNOWN = "unknown"

class ConstraintStatus(str, Enum):
    """Status of individual constraint fulfillment"""
    OK = "OK"
    MIN_NOT_MET = "MIN_NOT_MET"
    MAX_EXCEEDED = "MAX_EXCEEDED"
    EXACTLY_MET = "EXACTLY_MET"

class SolverName(str, Enum):
    """Supported solvers for linear optimization"""
    CBC = "CBC"
    GLPK = "GLPK"
    PULP_CBC_CMD = "PULP_CBC_CMD"
    GLPK_CMD = "GLPK_CMD"

class ObjectiveType(str, Enum):
    """Types of optimization objectives"""
    LEAST_COST = "least_cost"
    MAXIMIZE_NUTRIENT_DENSITY = "maximize_nutrient_density"
    MINIMIZE_PHOSPHORUS_EXCRETION = "minimize_phosphorus_excretion"