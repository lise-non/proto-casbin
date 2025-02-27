import casbin
import os
from ..config import settings

class CasbinEnforcer:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls._create_enforcer()
        return cls._instance
    
    @classmethod
    def _create_enforcer(cls):
        model_path = settings.CASBIN_MODEL_PATH
        policy_path = settings.CASBIN_POLICY_PATH
        
        # Ensure the model and policy files exist
        if not os.path.exists(model_path) or not os.path.exists(policy_path):
            raise FileNotFoundError(f"Casbin model or policy file not found: {model_path}, {policy_path}")
        
        return casbin.Enforcer(model_path, policy_path)
    
    @classmethod
    def enforce(cls, sub, obj, act):
        """Check if a user has permission to access a resource"""
        enforcer = cls.get_instance()
        return enforcer.enforce(sub, obj, act)
    
    @classmethod
    def add_role_for_user(cls, user, role):
        """Add a role for a user"""
        enforcer = cls.get_instance()
        return enforcer.add_grouping_policy(user, role)
    
    @classmethod
    def delete_role_for_user(cls, user, role):
        """Remove a role from a user"""
        enforcer = cls.get_instance()
        return enforcer.remove_grouping_policy(user, role)
    
    @classmethod
    def get_roles_for_user(cls, user):
        """Get all roles for a user"""
        enforcer = cls.get_instance()
        return enforcer.get_roles_for_user(user)
    
    @classmethod
    def add_policy(cls, role, resource, action):
        """Add a policy for a role"""
        enforcer = cls.get_instance()
        return enforcer.add_policy(role, resource, action)
    
    @classmethod
    def remove_policy(cls, role, resource, action):
        """Remove a policy"""
        enforcer = cls.get_instance()
        return enforcer.remove_policy(role, resource, action)
    
    @classmethod
    def get_permissions_for_user(cls, user):
        """Get all permissions for a user"""
        enforcer = cls.get_instance()
        return enforcer.get_permissions_for_user(user)
    
    @classmethod
    def save_policy(cls):
        """Save policy changes back to the policy file"""
        enforcer = cls.get_instance()
        return enforcer.save_policy()