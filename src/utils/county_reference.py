#!/usr/bin/env python3
"""
County reference and matching utilities for FDIC bank branch reports.
Provides exact county names from the database and improved matching logic.
"""

from src.utils.bq_utils import get_available_counties
from typing import List, Optional

def get_fallback_counties() -> List[str]:
    """Get a fallback list of counties for local development when BigQuery is not available."""
    return [
        "Montgomery County, Maryland",
        "Prince George's County, Maryland",
        "Baltimore County, Maryland",
        "Anne Arundel County, Maryland",
        "Howard County, Maryland",
        "Los Angeles County, California",
        "San Diego County, California",
        "Orange County, California",
        "Riverside County, California",
        "San Bernardino County, California",
        "Cook County, Illinois",
        "DuPage County, Illinois",
        "Lake County, Illinois",
        "Will County, Illinois",
        "Kane County, Illinois",
        "Harris County, Texas",
        "Dallas County, Texas",
        "Tarrant County, Texas",
        "Bexar County, Texas",
        "Travis County, Texas",
        "Miami-Dade County, Florida",
        "Broward County, Florida",
        "Palm Beach County, Florida",
        "Hillsborough County, Florida",
        "Orange County, Florida",
        "King County, Washington",
        "Pierce County, Washington",
        "Snohomish County, Washington",
        "Spokane County, Washington",
        "Clark County, Washington",
        "Maricopa County, Arizona",
        "Pima County, Arizona",
        "Pinal County, Arizona",
        "Yavapai County, Arizona",
        "Yuma County, Arizona",
        "Orleans Parish, Louisiana",
        "Jefferson Parish, Louisiana",
        "East Baton Rouge Parish, Louisiana",
        "St. Tammany Parish, Louisiana",
        "Lafayette Parish, Louisiana",
        "Caddo Parish, Louisiana",
        "Wayne County, Michigan",
        "Oakland County, Michigan",
        "Macomb County, Michigan",
        "Kent County, Michigan",
        "Genesee County, Michigan",
        "New York County, New York",
        "Kings County, New York",
        "Queens County, New York",
        "Bronx County, New York",
        "Richmond County, New York",
        "Nassau County, New York",
        "Suffolk County, New York",
        "Westchester County, New York",
        "Rockland County, New York",
        "Philadelphia County, Pennsylvania",
        "Allegheny County, Pennsylvania",
        "Montgomery County, Pennsylvania",
        "Bucks County, Pennsylvania",
        "Delaware County, Pennsylvania",
        "Lancaster County, Pennsylvania",
        "Chester County, Pennsylvania",
        "Lehigh County, Pennsylvania",
        "Northampton County, Pennsylvania",
        "Berks County, Pennsylvania",
        "Cuyahoga County, Ohio",
        "Franklin County, Ohio",
        "Hamilton County, Ohio",
        "Summit County, Ohio",
        "Montgomery County, Ohio",
        "Lucas County, Ohio",
        "Butler County, Ohio",
        "Stark County, Ohio",
        "Lorain County, Ohio",
        "Mahoning County, Ohio",
        "Fulton County, Georgia",
        "Gwinnett County, Georgia",
        "Cobb County, Georgia",
        "DeKalb County, Georgia",
        "Clayton County, Georgia",
        "Chatham County, Georgia",
        "Richmond County, Georgia",
        "Muscogee County, Georgia",
        "Bibb County, Georgia",
        "Houston County, Georgia"
    ]

def get_all_counties() -> List[str]:
    """Get all available counties from the database, with fallback for local development."""
    try:
        return get_available_counties()
    except Exception as e:
        print(f"Warning: Could not fetch counties from BigQuery: {e}")
        print("Using fallback county list for local development.")
        return get_fallback_counties()

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