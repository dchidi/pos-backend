from typing import List, Dict, Any

def filter_super_admin(groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter out super_admin group from the response"""
    return [group for group in groups if group["group"] != "super_admin"]