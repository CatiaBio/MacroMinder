import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

# Paths to JSON files
data_file = "user_data.json"
tracking_file = "daily_calorie_tracking.json"

# Predefined diet macro percentages
diets = {
    "Balanced": {"Protein": 25, "Fat": 30, "Carbs": 45},
    "Low-Carb": {"Protein": 30, "Fat": 50, "Carbs": 20},
    "High-Protein": {"Protein": 35, "Fat": 25, "Carbs": 40},
    "Ketogenic": {"Protein": 20, "Fat": 75, "Carbs": 5},
    "Mediterranean": {"Protein": 20, "Fat": 35, "Carbs": 45},
    "Custom": {"Protein": 0, "Fat": 0, "Carbs": 0}  # Placeholder for custom entry
}

# Load JSON data from file
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

# Save JSON data to file
def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def calculate_tdee_and_macros():
    try:
        # Check if all required fields are filled and contain numeric values
        user_name = name_entry.get().strip()
        if not user_name:
            raise ValueError("Please enter a name.")
        
        # Ensure numeric values are provided for weight, height, and age
        try:
            weight = float(weight_entry.get())
        except ValueError:
            raise ValueError("Please enter a valid number for weight.")
        
        try:
            height = float(height_entry.get())
        except ValueError:
            raise ValueError("Please enter a valid number for height.")
        
        try:
            age = int(age_entry.get())
        except ValueError:
            raise ValueError("Please enter a valid integer for age.")
        
        # Ensure macronutrient percentages are valid numbers
        try:
            protein_per = float(protein_entry.get())
            fat_per = float(fat_entry.get())
            carbs_per = float(carb_entry.get())
        except ValueError:
            raise ValueError("Please enter valid numbers for macronutrient percentages.")
        
        # Ensure the sum of macros is 100
        if protein_per + fat_per + carbs_per != 100:
            raise ValueError("The sum of protein, fat, and carbohydrate percentages must be 100.")
        
        gender = gender_var.get().lower()
        activity = activity_var.get()
        diet_type = diet_var.get()

        # Activity level dictionary
        activity_level = {
            "sedentary": 1.2,
            "lightly active": 1.375,
            "moderately active": 1.55,
            "very active": 1.725,
            "super active": 1.9
        }
        
        # Calculate BMR
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "m" else -161)
        
        # Calculate TDEE
        tdee = bmr * activity_level.get(activity, 1.2)
        
        # Get weight loss goal and calculate daily deficit
        weight_loss_goal = weight_loss_var.get()
        if weight_loss_goal == "0.5 kg":
            daily_deficit = 500
        elif weight_loss_goal == "0.75 kg":
            daily_deficit = 750
        elif weight_loss_goal == "1 kg":
            daily_deficit = 1000
        else:
            messagebox.showerror("Input Error", "Please select a valid weight loss goal")
            return
        
        # Calculate adjusted calorie intake for weight loss
        adjusted_calories = tdee - daily_deficit

        # Set warning if adjusted calories fall below BMR
        warning_textbox.config(state="normal")
        warning_textbox.delete(1.0, tk.END)
        if adjusted_calories < bmr:
            warning_message = ("Warning: Adjusted calories are below your BMR. "
                               "Avoid long-term intake below BMR to prevent deficiencies.\n"
                               "Limit deficit to 12-16 weeks; take diet breaks to prevent metabolic slowdown.\n"
                               "Source: Trexler et al., 2014.")
            warning_textbox.insert(tk.END, warning_message)
        else:
            warning_textbox.insert(tk.END, "")
        warning_textbox.config(state="disabled")

        # Calculate adjusted macros based on the new calorie goal
        protein_macros = (adjusted_calories * (protein_per / 100)) / 4
        fat_macros = (adjusted_calories * (fat_per / 100)) / 9
        carb_macros = (adjusted_calories * (carbs_per / 100)) / 4
        
        # Display results
        result_label.config(text=f"BMR: {int(bmr)} calories\n"
                                 f"Daily Energy Expenditure (TDEE): {int(tdee)} calories\n"
                                 f"Adjusted Calories for Goal: {int(adjusted_calories)} calories\n"
                                 f"Protein: {int(protein_macros)} g\n"
                                 f"Fat: {int(fat_macros)} g\n"
                                 f"Carbohydrates: {int(carb_macros)} g")
        
        # Prepare entry data with a timestamp and selected diet type, including macros if custom
        entry_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "weight": weight,
            "height": height,
            "age": age,
            "gender": gender,
            "activity": activity,
            "weight_loss_goal": weight_loss_goal,
            "diet_type": {
                "name": diet_type,
                "protein_per": protein_per if diet_type == "Custom" else diets[diet_type]["Protein"],
                "fat_per": fat_per if diet_type == "Custom" else diets[diet_type]["Fat"],
                "carb_per": carbs_per if diet_type == "Custom" else diets[diet_type]["Carbs"]
            },
            "results": {
                "bmr": int(bmr),
                "tdee": int(tdee),
                "adjusted_calories": int(adjusted_calories),
                "protein_g": int(protein_macros),
                "fat_g": int(fat_macros),
                "carb_g": int(carb_macros)
            }
        }

        # Save profile data with user's name as ID and entry data as history
        data = load_data(data_file)
        if user_name in data:
            data[user_name]["history"].append(entry_data)
        else:
            data[user_name] = {"history": [entry_data]}
        
        save_data(data_file, data)
        messagebox.showinfo("Profile Saved", "Your profile has been saved.")
        
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# Callback function to update macronutrient percentages based on diet selection
def on_diet_change(*args):
    selected_diet = diet_var.get()
    if selected_diet in diets:
        # Update the entries with the corresponding percentages
        protein_entry.delete(0, tk.END)
        protein_entry.insert(0, diets[selected_diet]["Protein"])
        
        fat_entry.delete(0, tk.END)
        fat_entry.insert(0, diets[selected_diet]["Fat"])
        
        carb_entry.delete(0, tk.END)
        carb_entry.insert(0, diets[selected_diet]["Carbs"])

# Display Profile with macronutrient percentages
def display_profile():
    clear_frame()
    
    tk.Label(root, text="Name:").grid(row=0, column=0)
    name_entry.grid(row=0, column=1)
    tk.Label(root, text="Weight (kg):").grid(row=1, column=0)
    weight_entry.grid(row=1, column=1)
    tk.Label(root, text="Height (cm):").grid(row=2, column=0)
    height_entry.grid(row=2, column=1)
    tk.Label(root, text="Age:").grid(row=3, column=0)
    age_entry.grid(row=3, column=1)
    tk.Label(root, text="Gender (m/f):").grid(row=4, column=0)
    tk.Radiobutton(root, text="Male", variable=gender_var, value="m").grid(row=4, column=1)
    tk.Radiobutton(root, text="Female", variable=gender_var, value="f").grid(row=4, column=2)
    
    tk.Label(root, text="Activity Level:").grid(row=5, column=0)
    activity_menu.grid(row=5, column=1)
    
    tk.Label(root, text="Diet Type:").grid(row=6, column=0)
    diet_menu.grid(row=6, column=1)

    # Update diet percentages when diet type changes
    diet_var.trace("w", on_diet_change)

    tk.Label(root, text="Desired Weight Loss per Week:").grid(row=7, column=0)
    weight_loss_menu = tk.OptionMenu(root, weight_loss_var, "0.5 kg", "0.75 kg", "1 kg")
    weight_loss_menu.grid(row=7, column=1)

    # Macronutrient percentages (with custom entries)
    tk.Label(root, text="Protein %:").grid(row=8, column=0)
    protein_entry.grid(row=8, column=1)

    tk.Label(root, text="Fat %:").grid(row=9, column=0)
    fat_entry.grid(row=9, column=1)

    tk.Label(root, text="Carbs %:").grid(row=10, column=0)
    carb_entry.grid(row=10, column=1)

    submit_button = tk.Button(root, text="Save Profile", command=calculate_tdee_and_macros)
    submit_button.grid(row=11, column=0, columnspan=2)

def display_objectives(results):
    clear_frame()
    
    tk.Label(root, text="Your Objectives").grid(row=0, column=0, columnspan=2, pady=10)
    tk.Label(root, text=f"BMR: {results['bmr']} calories").grid(row=1, column=0, columnspan=2)
    tk.Label(root, text=f"TDEE: {results['tdee']} calories").grid(row=2, column=0, columnspan=2)
    tk.Label(root, text=f"Adjusted Calories for Weight Loss Goal: {results['adjusted_calories']} calories").grid(row=3, column=0, columnspan=2)
    
    tk.Label(root, text=f"Protein: {results['protein_g']} g").grid(row=4, column=0, columnspan=2)
    tk.Label(root, text=f"Fat: {results['fat_g']} g").grid(row=5, column=0, columnspan=2)
    tk.Label(root, text=f"Carbohydrates: {results['carb_g']} g").grid(row=6, column=0, columnspan=2)
    
    tk.Button(root, text="Back to Profile", command=display_profile).grid(row=7, column=0, columnspan=2, pady=10)

# Check if user profile exists and load the last profile data if available
def load_last_profile():
    data = load_data(data_file)
    if data:
        # Get the last updated profile (latest entry for any user)
        for user_name, user_data in data.items():
            last_entry = user_data["history"][-1]
            name_entry.insert(0, user_name)
            weight_entry.insert(0, last_entry["weight"])
            height_entry.insert(0, last_entry["height"])
            age_entry.insert(0, last_entry["age"])
            gender_var.set(last_entry["gender"])
            activity_var.set(last_entry["activity"])
            diet_var.set(last_entry["diet_type"]["name"])
            weight_loss_var.set(last_entry["weight_loss_goal"])
            protein_entry.insert(0, last_entry["diet_type"]["protein_per"])
            fat_entry.insert(0, last_entry["diet_type"]["fat_per"])
            carb_entry.insert(0, last_entry["diet_type"]["carb_per"])

# Function to display objectives from saved profile data
def display_objectives_from_data():
    data = load_data(data_file)
    user_name = name_entry.get().strip()
    if user_name in data:
        # Load latest objectives
        last_entry = data[user_name]["history"][-1]
        display_objectives(last_entry["results"])
    else:
        messagebox.showerror("Error", "No profile data found. Please set up your profile first.")

# Main application setup
root = tk.Tk()
root.title("Health Tracker")

# Variables and UI elements
name_entry = tk.Entry(root)
weight_entry = tk.Entry(root)
height_entry = tk.Entry(root)
age_entry = tk.Entry(root)
gender_var = tk.StringVar(value="m")
activity_var = tk.StringVar(value="sedentary")
activity_menu = tk.OptionMenu(root, activity_var, "sedentary", "lightly active", "moderately active", "very active", "super active")
diet_var = tk.StringVar(value="Balanced")  # Default value
diet_menu = tk.OptionMenu(root, diet_var, *diets.keys())
protein_entry = tk.Entry(root)
fat_entry = tk.Entry(root)
carb_entry = tk.Entry(root)
weight_loss_var = tk.StringVar(value="0.5 kg")
protein_entry = tk.Entry(root)
fat_entry = tk.Entry(root)
carb_entry = tk.Entry(root)

# Result label and warning textbox for displaying TDEE and macros
result_label = tk.Label(root, text="")
result_label.grid(row=11, column=0, columnspan=3)
warning_textbox = tk.Text(root, height=5, width=50, wrap="word", fg="red")
warning_textbox.grid(row=12, column=0, columnspan=3)
warning_textbox.config(state="disabled")  # Make it read-only

# Daily tracking entries for calories and exercise
calories_entry = tk.Entry(root)
exercise_entry = tk.Entry(root)

# Function for daily tracking of calories and weight loss estimation
def display_daily_tracking():
    clear_frame()
    tk.Label(root, text="Enter Calories Consumed Today:").grid(row=0, column=0)
    calories_entry.grid(row=0, column=1)
    
    tk.Label(root, text="Enter Calories Burned Through Exercise:").grid(row=1, column=0)
    exercise_entry.grid(row=1, column=1)
    
    calculate_button = tk.Button(root, text="Save Daily Tracking and Estimate 5-Week Weight Loss", command=calculate_weight_loss)
    calculate_button.grid(row=2, column=0, columnspan=2)

def calculate_weight_loss():
    user_name = name_entry.get().strip()
    try:
        daily_calories = float(calories_entry.get())
        exercise_calories = float(exercise_entry.get())
        
        # Load the most recent profile data
        latest_data = load_data(data_file).get(user_name, {}).get("history", [])[-1]
        if not latest_data:
            messagebox.showerror("Error", "No profile data found. Please set up your profile first.")
            return

        tdee = latest_data["results"]["tdee"]
        initial_weight = latest_data["weight"]
        daily_deficit = tdee - (daily_calories - exercise_calories)

        # Calculate projected weight change over 5 weeks
        weight_change = (daily_deficit * 7 * 5) / 7700
        projected_weight = initial_weight - weight_change
        
        # Save daily tracking data with timestamp
        tracking_data = load_data(tracking_file)
        daily_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "calories_consumed": daily_calories,
            "calories_burned": exercise_calories,
            "net_calories": daily_calories - exercise_calories,
            "daily_deficit": daily_deficit
        }
        
        if user_name in tracking_data:
            tracking_data[user_name].append(daily_entry)
        else:
            tracking_data[user_name] = [daily_entry]
        
        save_data(tracking_file, tracking_data)

        messagebox.showinfo("Weight Loss Estimate", f"Projected weight after 5 weeks: {projected_weight:.2f} kg")
        
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# Function to clear the frame
def clear_frame():
    for widget in root.winfo_children():
        widget.grid_remove()

# Menu setup and main application setup
main_menu = tk.Menu(root)
root.config(menu=main_menu)

profile_menu = tk.Menu(main_menu, tearoff=0)
profile_menu.add_command(label="Set Up Profile", command=display_profile)
profile_menu.add_command(label="Daily Tracking", command=display_daily_tracking)
profile_menu.add_command(label="View Objectives", command=display_objectives_from_data)
main_menu.add_cascade(label="Options", menu=profile_menu)

# Load last profile on app start if data exists
load_last_profile()

# Start Tkinter main loop
root.mainloop()