from destinations import load_destinations

def get_recommendations(budget, travel_month, highlights=None):
    """Get recommendations based on budget, time, and highlights."""
    destinations = load_destinations()
    
    # Filter destinations
    filtered = []
    for dest in destinations:
        # Budget check
        if dest["Min_Budget"] <= budget <= dest["Max_Budget"]:
            # Best time check
            if travel_month in dest["Best_Time_Months"]:
                # Highlights check (if provided)
                if not highlights or any(h.lower() in dest["Highlights"].lower() for h in highlights.split(",")):
                    filtered.append(dest)
    
    # Sort by budget (ascending), then highlights match, then destination
    filtered.sort(key=lambda x: (
        x["Min_Budget"], 
        -sum(h.lower() in x["Highlights"].lower() for h in (highlights.split(",") if highlights else [])), 
        x["Destination"]
    ))
    
    return filtered