# utils.py
"""
Shared utility functions used across the application.
"""
from db.db_config import CONFIG_PARAM_DISPLAY


def build_config_params_label(config_params):
    """
    Build a label string from explicitly selected configuration parameters.
    Only includes parameters that were explicitly chosen by the user.
    
    This function is used by both query_handlers.py and plotting.py to avoid
    code duplication.
    
    Args:
        config_params (dict): Dictionary with keys 'pg', 'cp', 'bpc', 'cf', 'qg'
                              each containing a list of selected values
    
    Returns:
        str: Formatted label string for x-axis
    """
    if not config_params:
        return "All Configurations"
    
    label_parts = []
    
    # Plan Generator
    pg = config_params.get('pg', [])
    if pg and len(pg) > 0:
        label_parts.append(f"PG: {', '.join(pg)}")
    
    # Cardinality Provider
    cp = config_params.get('cp', [])
    if cp and len(cp) > 0:
        label_parts.append(f"CP: {', '.join(cp)}")
    
    # Build Plan Class
    bpc = config_params.get('bpc', [])
    if bpc and len(bpc) > 0:
        label_parts.append(f"BPC: {', '.join(bpc)}")
    
    # Query Graph (for query mode)
    qg = config_params.get('qg', [])
    if qg and len(qg) > 0:
        label_parts.append(f"Query: {', '.join(qg)}")
    
    # Cost Functions (from nested dict)
    cf = config_params.get('cf', {})
    if cf:
        for cf_key, cf_values in cf.items():
            if cf_values and len(cf_values) > 0:
                # Format the cost function name nicely
                cf_name = cf_key.replace('bpi_cf_', '').replace('wp_cf_', '').replace('_', ' ').title()
                label_parts.append(f"{cf_name}: {', '.join(cf_values)}")
    
    if label_parts:
        return '\n'.join(label_parts)
    else:
        return "All Configurations"
