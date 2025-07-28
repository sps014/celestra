"""Networking module for Celestraa DSL."""

from .service import Service
from .ingress import Ingress
from .companion import Companion
from .scaling import Scaling
from .health import Health
from .network_policy import NetworkPolicy

__all__ = [
    "Service", 
    "Ingress", 
    "Companion", 
    "Scaling", 
    "Health", 
    "NetworkPolicy"
] 