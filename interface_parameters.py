# interface_parameters.py
import tkinter as tk
from tkinter import messagebox
from sir import create_SIR_simulation
from sis import create_SIS_simulation
from SEIR import create_SEIR_simulation
from seirs import create_SEIRS_simulation
from sird import create_SIRD_simulation
from seird import create_SEIRD_simulation

def on_generate():
    try:
        # Get selected model
        model = model_var.get()

        # Get values from the inputs
        S0 = susceptible_var.get()
        I0 = infected_var.get()
        beta = beta_var.get()
        gamma = gamma_var.get() 
        days = days_var.get()
        sigma = sigma_var.get()
        mu = mu_var.get()

        # Check for empty fields
        if not all([S0, I0, beta, days, gamma]) or (model == "SEIRD" and not all([10])):
            print("Error: One or more fields are empty!")
            messagebox.showerror("Input Error", "Please fill in all fields before generating.")
            return

        # Convert inputs to proper types
        S0 = int(S0)
        I0 = int(I0)
        beta = float(beta)
        gamma = float(gamma)
        sigma = float(sigma) if model == 'SEIRD' else 0
        mu = float(mu) if model == 'SEIRD' else 0
        days = int(days)

        # Log to console
        print(f"Generating simulation with parameters: Model={model}, S0={S0}, I0={I0}, Beta={beta}, Gamma={gamma}, Days={days}")

        # Run the selected simulation
        if model == "SIR":
            create_SIR_simulation(number_of_people=S0, num_infected=I0, infect_rate=beta, recover_rate=gamma, max_days=days)
        elif model == "SIS":
            create_SIS_simulation(number_of_people=S0, num_infected=I0, infect_rate=beta, recover_rate=gamma, max_days=days)
        elif model == "SEIR":
            create_SEIR_simulation(number_of_people=S0, num_infected=I0, infect_rate=beta, recover_rate=gamma,
                                   progression_rate=sigma, max_days=days)
        elif model == "SEIRS":
            create_SEIRS_simulation(number_of_people=S0, num_infected=I0, infect_rate=beta, recover_rate=gamma,
                                    lose_immunity_rate=mu, progression_rate=sigma, max_days=days)
        elif model == "SIRD":
            create_SIRD_simulation(number_of_people=S0, num_infected=I0, infect_rate=beta, recover_rate=gamma,
                                    mortality_rate=mu, max_days=days)
        elif model == "SEIRD":
            create_SEIRD_simulation(number_of_people=S0, num_infected=I0, infect_rate=beta, recover_rate=gamma,
                                    mortality_rate=mu, progression_rate=sigma, max_days=days)
        
        # Notify the user
        messagebox.showinfo("Success", "Simulation and GIF generation complete!")
    except ValueError as e:
        print(f"Input Error: {e}")
        messagebox.showerror("Input Error", f"Invalid input: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")


# Create the main application window
root = tk.Tk()
root.title("Epidemic Model Simulation")

# Define input variables
susceptible_var = tk.StringVar()
infected_var = tk.StringVar()
recovered_var = tk.StringVar()
beta_var = tk.StringVar()
gamma_var = tk.StringVar()
sigma_var = tk.StringVar()
mu_var = tk.StringVar()
days_var = tk.StringVar()
max_days_var = tk.StringVar()

# Add a dropdown menu for model selection
model_var = tk.StringVar(value="SIR")  # Default model is SIR
model_label = tk.Label(root, text="Choose Model:")
model_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

model_dropdown = tk.OptionMenu(root, model_var, "SIR", "SIS", "SIRD", "SEIR", "SEIRS", "SEIRD")
model_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# Create and arrange input fields for SIR and SIS models
fields = [
    ("Initial Susceptible Population (S0):", susceptible_var),
    ("Initial Infected Population (I0):", infected_var),
    ("Infection Rate (Beta):", beta_var),
    ("Number of Days to Simulate:", days_var),
    ("Recovery Rate (Gamma):", gamma_var)
]

seird_fields = [
    ("Progression Rate(Sigma)", sigma_var),
    ("Death Rate(Mu)", mu_var)
]

seir_fields = [
    ("Progression Rate(Sigma)", sigma_var)
]

seirs_fields = [
    ("Progression Rate(Sigma)", sigma_var),
    ("Immunity Loss Rate(Mu)", mu_var)
]

sird_fields = [
    ("Death Rate(Mu)", mu_var)
]

def focus_next(event):
    # move to next widget on down arrow
    event.widget.tk_focusNext().focus()
    return "break"

def focus_previous(event):
    # move to next widget on up arrow
    event.widget.tk_focusPrev().focus()
    return "break"

def create_fields():
    
    for idx, (label_text, var) in enumerate(fields):
        label = tk.Label(root, text=label_text)
        label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky="e")

        entry = tk.Entry(root, textvariable=var)
        entry.grid(row=idx + 1, column=1, padx=10, pady=5, sticky="w")
        
        entry.bind("<Down>", focus_next)
        entry.bind("<Up>", focus_previous)

    if model_var.get() == "SEIR":
        for idx, (label_text, var) in enumerate(seir_fields):
            label = tk.Label(root, text=label_text)
            label.grid(row=idx + len(fields) + 1, column=0, padx=10, pady=5, sticky="e")

            entry = tk.Entry(root, textvariable=var)
            entry.grid(row=idx + len(fields) + 1, column=1, padx=10, pady=5, sticky="w")
            
            entry.bind("<Down>", focus_next)
            entry.bind("<Up>", focus_previous)

    if model_var.get() == "SEIRS":
        for idx, (label_text, var) in enumerate(seirs_fields):
            label = tk.Label(root, text=label_text)
            label.grid(row=idx + len(fields) + len(seirs_fields) + 1, column=0, padx=10, pady=5, sticky="e")

            entry = tk.Entry(root, textvariable=var)
            entry.grid(row=idx + len(fields) + len(seirs_fields) + 1, column=1, padx=10, pady=5, sticky="w")
            
            entry.bind("<Down>", focus_next)
            entry.bind("<Up>", focus_previous)

    if model_var.get() == "SIRD":
        for idx, (label_text, var) in enumerate(sird_fields):
            label = tk.Label(root, text=label_text)
            label.grid(row=idx + len(fields) + len(sird_fields) + 1, column=0, padx=10, pady=5, sticky="e")

            entry = tk.Entry(root, textvariable=var)
            entry.grid(row=idx + len(fields) + len(sird_fields) + 1, column=1, padx=10, pady=5, sticky="w")
            
            entry.bind("<Down>", focus_next)
            entry.bind("<Up>", focus_previous)

    if model_var.get() == "SEIRD":
        for idx, (label_text, var) in enumerate(seird_fields):
            label = tk.Label(root, text=label_text)
            label.grid(row=idx + len(fields) + len(seird_fields) + 1, column=0, padx=10, pady=5, sticky="e")

            entry = tk.Entry(root, textvariable=var)
            entry.grid(row=idx + len(fields) + len(seird_fields) + 1, column=1, padx=10, pady=5, sticky="w")
            
            entry.bind("<Down>", focus_next)
            entry.bind("<Up>", focus_previous)



# field update for model selection
def update_fields(*args):
    # Clear previous fields
    for widget in root.winfo_children():
        widget.grid_forget()

    # dropdown logic
    model_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
    model_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    create_fields()

    # generate button
    generate_button = tk.Button(root, text="Generate", command=on_generate)
    generate_button.grid(row=len(fields) +
                             (len(seirs_fields) if model_var.get() == "SEIRS" else 0) +
                             (len(sird_fields) if model_var.get() == "SIRD" else 0) +
                             (len(seir_fields) if model_var.get() == "SEIR" else 0) +
                             (len(seird_fields) if model_var.get() == "SEIRD" else 0)
                             + 3, column=0, columnspan=2, pady=10)


# bind model selection
model_var.trace("w", update_fields)

# init call for field update
update_fields()

# start event loop
root.bind("<Return>", lambda event: on_generate()) # funny QoL stuff
root.mainloop()
