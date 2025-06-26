#!/usr/bin/env python3
"""
County reference and matching utilities for FDIC bank branch reports.
Provides exact county names from the database and improved matching logic.
"""

from src.utils.bq_utils import get_available_counties
from typing import List, Optional

def get_all_counties() -> List[str]:
    """Get all available counties from the database."""
    return get_available_counties()

def find_county_matches(search_term: str, limit: int = 10) -> List[str]:
    """
    Find counties that match a search term.
    
    Args:
        search_term: Partial county name to search for
        limit: Maximum number of results to return
        
    Returns:
        List of matching counties
    """
    counties = get_all_counties()
    search_lower = search_term.lower()
    
    matches = []
    for county in counties:
        if search_lower in county.lower():
            matches.append(county)
            if len(matches) >= limit:
                break
    
    return matches

def get_counties_by_state(state_abbr: str) -> List[str]:
    """
    Get all counties for a specific state.
    
    Args:
        state_abbr: State abbreviation (e.g., 'CA', 'IL', 'NY')
        
    Returns:
        List of counties in that state
    """
    counties = get_all_counties()
    state_lower = state_abbr.lower()
    
    return [county for county in counties if county.lower().endswith(f", {state_lower}")]

def find_exact_county(county_name: str, state_abbr: str = None) -> Optional[str]:
    """
    Find the exact county name from the database.
    
    Args:
        county_name: County name (e.g., "Los Angeles", "Cook")
        state_abbr: State abbreviation (e.g., "CA", "IL") - optional but recommended
        
    Returns:
        Exact county name from database or None if not found
    """
    counties = get_all_counties()
    county_lower = county_name.lower()
    
    if state_abbr:
        state_lower = state_abbr.lower()
        # Look for exact match with state
        for county in counties:
            if (county_lower in county.lower() and 
                county.lower().endswith(f", {state_lower}")):
                return county
    
    # If no state specified or no match found, return first partial match
    for county in counties:
        if county_lower in county.lower():
            return county
    
    return None

def print_county_reference():
    """Print a reference of all available counties."""
    counties = get_all_counties()
    
    print("=" * 80)
    print("AVAILABLE COUNTIES IN DATABASE")
    print("=" * 80)
    print(f"Total counties: {len(counties)}")
    print()
    
    # Group by state
    states = {}
    for county in counties:
        state = county.split(", ")[-1]
        if state not in states:
            states[state] = []
        states[state].append(county)
    
    # Print by state
    for state in sorted(states.keys()):
        print(f"\n{state}:")
        for county in sorted(states[state]):
            print(f"  {county}")

def main():
    """Main function for county reference utilities."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            print_county_reference()
        elif command == "search" and len(sys.argv) > 2:
            search_term = sys.argv[2]
            matches = find_county_matches(search_term)
            print(f"Counties matching '{search_term}':")
            for match in matches:
                print(f"  {match}")
        elif command == "state" and len(sys.argv) > 2:
            state = sys.argv[2]
            counties = get_counties_by_state(state)
            print(f"Counties in {state}:")
            for county in counties:
                print(f"  {county}")
        else:
            print("Usage:")
            print("  python county_reference.py list                    # List all counties")
            print("  python county_reference.py search <term>          # Search counties")
            print("  python county_reference.py state <abbr>           # Counties by state")
    else:
        print("County Reference Utilities")
        print("=" * 40)
        print("Available commands:")
        print("  list    - Show all counties")
        print("  search  - Search for counties")
        print("  state   - Show counties by state")
        print()
        print("Examples:")
        print("  python county_reference.py list")
        print("  python county_reference.py search Los Angeles")
        print("  python county_reference.py state CA")

if __name__ == "__main__":
    main() 