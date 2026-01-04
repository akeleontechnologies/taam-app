import os
from enum import Enum
import environ

env = environ.Env()

class DeploymentEnvironment(Enum):
    DEV = "dev"
    PROD = "prod"
    
    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        return cls.DEV  # Default to dev if not found
