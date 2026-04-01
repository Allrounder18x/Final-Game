"""
Domestic competitions and teams for top 10 Test-playing nations (all 3 formats).
Used by DomesticSystem to create domestic teams and generate fixtures.
"""

# Top 10 Test nations (by ICC status) - used for domestic competitions
TOP_10_TEST_NATIONS = [
    "India", "Australia", "England", "South Africa", "Pakistan",
    "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan"
]

# Domestic competitions per nation: { format: (competition_name, [team_names]) }
# Each nation has T20, ODI, and Test/FC domestic leagues.
DOMESTIC_COMPETITIONS = {
    "India": {
        "T20": ("IPL", [
            "Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bangalore",
            "Kolkata Knight Riders", "Delhi Capitals", "Punjab Kings",
            "Rajasthan Royals", "Sunrisers Hyderabad", "Gujarat Titans", "Lucknow Super Giants"
        ]),
        "ODI": ("Vijay Hazare Trophy", [
            "Mumbai", "Karnataka", "Delhi", "Tamil Nadu", "Bengal", "Hyderabad",
            "Punjab", "Kerala", "Baroda", "Saurashtra"
        ]),
        "Test": ("Ranji Trophy", [
            "Mumbai", "Karnataka", "Delhi", "Tamil Nadu", "Bengal", "Hyderabad",
            "Punjab", "Kerala", "Baroda", "Saurashtra"
        ]),
    },
    "Australia": {
        "T20": ("Big Bash League", [
            "Sydney Sixers", "Sydney Thunder", "Melbourne Stars", "Melbourne Renegades",
            "Perth Scorchers", "Adelaide Strikers", "Brisbane Heat", "Hobart Hurricanes"
        ]),
        "ODI": ("Marsh Cup", [
            "New South Wales", "Victoria", "Queensland", "Western Australia",
            "South Australia", "Tasmania"
        ]),
        "Test": ("Sheffield Shield", [
            "New South Wales", "Victoria", "Queensland", "Western Australia",
            "South Australia", "Tasmania"
        ]),
    },
    "England": {
        "T20": ("T20 Blast", [
            "Surrey", "Middlesex", "Essex", "Hampshire", "Kent", "Lancashire",
            "Nottinghamshire", "Yorkshire", "Warwickshire", "Somerset"
        ]),
        "ODI": ("Royal London Cup", [
            "Surrey", "Middlesex", "Essex", "Hampshire", "Kent", "Lancashire",
            "Nottinghamshire", "Yorkshire", "Warwickshire", "Somerset"
        ]),
        "Test": ("County Championship", [
            "Surrey", "Middlesex", "Essex", "Hampshire", "Kent", "Lancashire",
            "Nottinghamshire", "Yorkshire", "Warwickshire", "Somerset"
        ]),
    },
    "South Africa": {
        "T20": ("SA20", [
            "MI Cape Town", "Paarl Royals", "Joburg Super Kings", "Pretoria Capitals",
            "Sunrisers Eastern Cape", "Durban Super Giants"
        ]),
        "ODI": ("One-Day Cup", [
            "Western Province", "Eastern Province", "Northerns", "KwaZulu-Natal",
            "Free State", "Boland", "North West", "Gauteng"
        ]),
        "Test": ("First Division", [
            "Western Province", "Eastern Province", "Northerns", "KwaZulu-Natal",
            "Free State", "Boland", "North West", "Gauteng"
        ]),
    },
    "Pakistan": {
        "T20": ("PSL", [
            "Islamabad United", "Karachi Kings", "Lahore Qalandars", "Multan Sultans",
            "Peshawar Zalmi", "Quetta Gladiators"
        ]),
        "ODI": ("Pakistan Cup", [
            "Central Punjab", "Southern Punjab", "Khyber Pakhtunkhwa", "Sindh",
            "Balochistan", "Northern"
        ]),
        "Test": ("Quaid-e-Azam Trophy", [
            "Central Punjab", "Southern Punjab", "Khyber Pakhtunkhwa", "Sindh",
            "Balochistan", "Northern"
        ]),
    },
    "New Zealand": {
        "T20": ("Super Smash", [
            "Auckland Aces", "Northern Brave", "Wellington Firebirds", "Canterbury Kings",
            "Central Stags", "Otago Volts"
        ]),
        "ODI": ("Ford Trophy", [
            "Auckland", "Northern Districts", "Wellington", "Canterbury",
            "Central Districts", "Otago"
        ]),
        "Test": ("Plunket Shield", [
            "Auckland", "Northern Districts", "Wellington", "Canterbury",
            "Central Districts", "Otago"
        ]),
    },
    "West Indies": {
        "T20": ("CPL", [
            "Barbados Royals", "Guyana Amazon Warriors", "Jamaica Tallawahs",
            "St Kitts & Nevis Patriots", "Saint Lucia Kings", "Trinidad & Tobago Knight Riders"
        ]),
        "ODI": ("Super50 Cup", [
            "Barbados", "Guyana", "Jamaica", "Leeward Islands", "Windward Islands",
            "Trinidad & Tobago"
        ]),
        "Test": ("First-Class Championship", [
            "Barbados", "Guyana", "Jamaica", "Leeward Islands", "Windward Islands",
            "Trinidad & Tobago"
        ]),
    },
    "Sri Lanka": {
        "T20": ("LPL", [
            "Colombo Strikers", "Dambulla Aura", "Galle Marvels", "Jaffna Kings",
            "Kandy Falcons"
        ]),
        "ODI": ("List A Premier", [
            "Colombo", "Kandy", "Galle", "Dambulla", "Jaffna", "Chilaw"
        ]),
        "Test": ("Premier League", [
            "Colombo", "Kandy", "Galle", "Dambulla", "Jaffna", "Chilaw"
        ]),
    },
    "Bangladesh": {
        "T20": ("BPL", [
            "Comilla Victorians", "Dhaka Dominators", "Fortune Barishal", "Khulna Tigers",
            "Rangpur Riders", "Sylhet Strikers"
        ]),
        "ODI": ("NCL One-Day", [
            "Dhaka Division", "Chittagong Division", "Rajshahi Division", "Khulna Division",
            "Sylhet Division", "Rangpur Division", "Barishal Division", "Dhaka Metropolis"
        ]),
        "Test": ("NCL First-Class", [
            "Dhaka Division", "Chittagong Division", "Rajshahi Division", "Khulna Division",
            "Sylhet Division", "Rangpur Division", "Barishal Division", "Dhaka Metropolis"
        ]),
    },
    "Afghanistan": {
        "T20": ("Shpageeza League", [
            "Kabul Eagles", "Kandahar Knights", "Balkh Legends", "Nangarhar Leopards",
            "Paktia Panthers", "Hindukush Stars"
        ]),
        "ODI": ("List A Regional", [
            "Kabul", "Kandahar", "Balkh", "Nangarhar", "Paktia", "Hindukush"
        ]),
        "Test": ("First-Class Regional", [
            "Kabul", "Kandahar", "Balkh", "Nangarhar", "Paktia", "Hindukush"
        ]),
    },
}


def nation_for_domestic_team_name(team_name: str):
    """
    Return the parent Test nation for an in-game domestic club name, or None if unknown.
    Used when merging Cricinfo rosters into domestic_custom_rosters.json.
    """
    if not team_name:
        return None
    for nation, comps in DOMESTIC_COMPETITIONS.items():
        for fmt in ("T20", "ODI", "Test"):
            if fmt not in comps:
                continue
            _, names = comps[fmt]
            if team_name in names:
                return nation
    return None
