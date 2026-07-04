import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Smart AC & Energy Estimator",
    page_icon=":zap:",
    layout="wide"
)

# Initialize session state for persistence
if 'advanced_mode' not in st.session_state:
    st.session_state.advanced_mode = False

# Sidebar Configuration
with st.sidebar:
    st.header("Smart AC & Energy Estimator")
    st.markdown("---")
    
    # Budget Input
    monthly_budget = st.number_input(
        "Monthly Target Budget (PKR)",
        min_value=1000.0,
        max_value=50000.0,
        value=10000.0,
        step=500.0,
        help="Set your target monthly budget for AC electricity consumption"
    )
    
    # AC Capacity
    ac_capacity = st.selectbox(
        "AC Capacity",
        ["1 Ton", "1.5 Ton", "2 Ton"],
        help="Select your air conditioner's cooling capacity"
    )
    
    # Daily Usage
    daily_hours = st.slider(
        "Daily Usage Hours",
        min_value=1,
        max_value=24,
        value=8,
        help="Average number of hours your AC runs per day"
    )
    
    # Tariff Rate
    tariff_rate = st.number_input(
        "Electricity Tariff Rate (PKR per Unit)",
        min_value=10.0,
        max_value=100.0,
        value=50.0,
        step=1.0,
        help="Current electricity rate per kWh unit. Default set to 50 PKR including taxes"
    )
    
    st.markdown("---")
    st.caption("Developed for Pakistan's major AC brands: TCL, Haier, Orient, Dawlance, Gree")

# Main Screen - Welcome Header
st.title("Smart Home Energy & AC Bill Estimator")
st.markdown(
    """
    Welcome to your comprehensive AC energy cost estimator. This tool helps you understand 
    your electricity consumption and provides smart optimization suggestions to keep your 
    bills within budget.
    """
)
st.markdown("---")

# Universal Brand & Ampere Logic - Advanced Mode Checkbox
advanced_mode = st.checkbox(
    "Does your AC support Ampere Control, Gear Mode, or ECO Limits (L1/L2/L3)?",
    help="Enable this if your AC has advanced power saving features like Eco modes or gear controls"
)

# Conditional Rendering
if advanced_mode:
    st.session_state.advanced_mode = True
    st.subheader("Advanced Multi-Brand Mode")
    st.markdown("Select your AC's active power gear or eco mode limit:")
    
    # Power Gear Selection
    power_mode = st.radio(
        "Select Active Power Gear / Eco Mode Limit",
        [
            "Low Saving / Full Power / L3 / 80% (approx. 8 Amperes)",
            "Medium Saving / Eco Mode / L2 / 60% (approx. 6 Amperes)",
            "Super Eco Mode / Max Saving / L1 / 40% (approx. 4 Amperes)"
        ],
        index=1,
        help="Choose the current operating mode of your AC. Higher amp draw means more power consumption."
    )
    
    # Map selections to amperes
    ampere_mapping = {
        "Low Saving / Full Power / L3 / 80% (approx. 8 Amperes)": 8.0,
        "Medium Saving / Eco Mode / L2 / 60% (approx. 6 Amperes)": 6.0,
        "Super Eco Mode / Max Saving / L1 / 40% (approx. 4 Amperes)": 4.0
    }
    current_amperes = ampere_mapping[power_mode]
    
    # Extract mode name for display
    mode_display = power_mode.split(" (")[0]
    
else:
    st.session_state.advanced_mode = False
    st.info("Standard Mode Active - Using baseline power consumption for typical inverter ACs")
    current_amperes = 3.5  # Standard baseline for multi-brand inverter
    mode_display = "Standard Inverter Mode"

# Core Calculations
VOLTAGE = 220  # Fixed household voltage in Pakistan

def calculate_energy_cost(amperes, hours, rate):
    """
    Calculate energy consumption and cost based on amperes, hours, and tariff rate
    """
    watts = amperes * VOLTAGE
    daily_units = (watts * hours) / 1000
    monthly_units = daily_units * 30
    monthly_bill = monthly_units * rate
    return {
        'watts': watts,
        'daily_units': daily_units,
        'monthly_units': monthly_units,
        'monthly_bill': monthly_bill,
        'amperes': amperes
    }

# Calculate current configuration
current_results = calculate_energy_cost(current_amperes, daily_hours, tariff_rate)

# Calculate Super Eco Mode savings (4 Amperes)
eco_results = calculate_energy_cost(4.0, daily_hours, tariff_rate)

# Savings calculation
monthly_savings = current_results['monthly_bill'] - eco_results['monthly_bill']
savings_percentage = (monthly_savings / current_results['monthly_bill']) * 100 if current_results['monthly_bill'] > 0 else 0

# Metrics Display
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Current Amperes Draw",
        value=f"{current_amperes:.1f} A",
        delta=f"{mode_display}"
    )

with col2:
    st.metric(
        label="Estimated Monthly Units (kWh)",
        value=f"{current_results['monthly_units']:.1f} kWh",
        delta=f"{current_results['daily_units']:.1f} kWh/day"
    )

with col3:
    st.metric(
        label="Estimated Monthly AC Bill",
        value=f"Rs. {current_results['monthly_bill']:,.0f}",
        delta=f"Rs. {monthly_savings:,.0f} savings with Eco mode"
    )

# Graphical Visualization
st.subheader("Monthly Cost Comparison")
st.markdown("Visual comparison of your current configuration vs. Super Eco Mode (4 Amperes)")

# Create comparison chart data
comparison_data = pd.DataFrame({
    'Configuration': ['Current Mode', 'Super Eco Mode'],
    'Monthly Bill (PKR)': [
        current_results['monthly_bill'],
        eco_results['monthly_bill']
    ]
})

# Create bar chart using matplotlib
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(comparison_data['Configuration'], comparison_data['Monthly Bill (PKR)'], 
              color=['#FF6B6B', '#4ECDC4'], width=0.6)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'Rs. {height:,.0f}', ha='center', va='bottom', fontweight='bold')

ax.set_ylabel('Monthly Bill (PKR)', fontsize=12)
ax.set_title('Energy Cost Comparison: Current Mode vs. Super Eco Mode', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, max(comparison_data['Monthly Bill (PKR)']) * 1.15)

# Add savings annotation
if monthly_savings > 0:
    ax.text(0.5, 0.95, f'Potential Monthly Savings: Rs. {monthly_savings:,.0f} ({savings_percentage:.1f}%)',
            transform=ax.transAxes, ha='center', fontsize=12,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.3))

plt.tight_layout()
st.pyplot(fig)

# Smart Saving Advice Container
st.subheader("Smart Saving Insights")

# Create columns for summary
col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Total Estimated Monthly Units",
        value=f"{current_results['monthly_units']:.1f} kWh",
        delta=f"At {tariff_rate:.1f} PKR/unit"
    )

with col2:
    st.metric(
        label="Estimated Monthly AC Bill",
        value=f"Rs. {current_results['monthly_bill']:,.0f}",
        delta=f"vs. target Rs. {monthly_budget:,.0f}"
    )

# Budget comparison and advice
if current_results['monthly_bill'] > monthly_budget:
    excess_amount = current_results['monthly_bill'] - monthly_budget
    st.warning(
        f"""
        **Alert**: Your estimated AC bill exceeds your target budget by **Rs. {excess_amount:,.0f}**.
        
        **Smart Optimization Advice:**
        - Consider shifting your AC to L1 / 40% Eco mode during sleeping hours to slash power draw
        - Reduce daily usage by 2-3 hours during peak tariff periods (5 PM - 11 PM)
        - Set your AC temperature to 24-26°C for optimal efficiency
        - Ensure regular maintenance (clean filters, coils) for better performance
        - Use timer functions to automatically turn off AC during non-peak hours
        """
    )
else:
    remaining_budget = monthly_budget - current_results['monthly_bill']
    st.success(
        f"""
        **Great News!** Your current configuration safely falls within budget limits.
        
        You have **Rs. {remaining_budget:,.0f}** remaining within your target budget.
        
        **Smart Saving Tip:** Even though you're within budget, you could save approximately 
        **Rs. {monthly_savings:,.0f}** per month by using Super Eco Mode (4 Amperes) consistently.
        """
    )

# Additional brand-specific information
with st.expander("About Multi-Brand Compatibility"):
    st.markdown("""
    This estimator supports major AC brands available in Pakistan:
    
    - **TCL**: Supports Eco modes and power saving features
    - **Haier**: Features Gear technology for optimized performance
    - **Orient**: Offers multiple power saving levels
    - **Dawlance**: Advanced Eco modes for energy efficiency
    - **Gree**: Comprehensive energy management systems
    
    The tool maps brand-specific terminologies (Gears, ECO %, L1/L2/L3) to standard Ampere draw values:
    - **Full Power / L3**: 8 Amperes (80% capacity)
    - **Eco Mode / L2**: 6 Amperes (60% capacity)  
    - **Super Eco / L1**: 4 Amperes (40% capacity)
    """
    )

# Footer
st.markdown("---")
st.caption("Smart Home Energy & AC Bill Estimator v1.0 | Developed for Pakistan's Electricity Market")
