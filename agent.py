import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import google.generativeai as genai
from datetime import datetime
import os
import json

class SalesAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sales Agent Assistant")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Configure the Gemini API
        self.api_key = tk.StringVar()
        self.configure_api_frame()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_prospect_tab()
        self.create_email_tab()
        self.create_followup_tab()
        self.create_objection_tab()
        self.create_proposal_tab()
        
        # Initialize the sales agent backend
        self.sales_agent = None
        self.prospects = {}
        self.current_prospect = None
        
        # Load existing prospects if any
        self.load_prospects()
        
    def configure_api_frame(self):
        api_frame = ttk.LabelFrame(self.root, text="API Configuration")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(api_frame, text="Gemini API Key:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(api_frame, textvariable=self.api_key, width=50, show="*").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(api_frame, text="Initialize API", command=self.initialize_api).grid(row=0, column=2, padx=5, pady=5)
        
    def initialize_api(self):
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter your Gemini API key")
            return
            
        try:
            genai.configure(api_key=self.api_key.get())
            self.sales_agent = SalesAgent(api_key=self.api_key.get())
            messagebox.showinfo("Success", "API initialized successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize API: {str(e)}")
    
    def create_prospect_tab(self):
        prospect_tab = ttk.Frame(self.notebook)
        self.notebook.add(prospect_tab, text="Prospect Management")
        
        # Left frame for list of prospects
        left_frame = ttk.Frame(prospect_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Prospects:").pack(anchor=tk.W)
        self.prospect_listbox = tk.Listbox(left_frame, width=30, height=20)
        self.prospect_listbox.pack(fill=tk.Y, expand=True)
        self.prospect_listbox.bind('<<ListboxSelect>>', self.load_prospect_details)
        
        ttk.Button(left_frame, text="New Prospect", command=self.clear_prospect_form).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="Delete Prospect", command=self.delete_prospect).pack(fill=tk.X)
        
        # Right frame for prospect details
        right_frame = ttk.LabelFrame(prospect_tab, text="Prospect Details")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Prospect form
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.prospect_name = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prospect_name, width=40).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Company
        ttk.Label(form_frame, text="Company:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.prospect_company = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prospect_company, width=40).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Role
        ttk.Label(form_frame, text="Role:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.prospect_role = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prospect_role, width=40).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Interests
        ttk.Label(form_frame, text="Interests:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.prospect_interests = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prospect_interests, width=40).grid(row=3, column=1, sticky=tk.W, pady=2)
        ttk.Label(form_frame, text="(Comma separated)").grid(row=3, column=2, sticky=tk.W, pady=2)
        
        # Pain points
        ttk.Label(form_frame, text="Pain Points:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.prospect_pain_points = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prospect_pain_points, width=40).grid(row=4, column=1, sticky=tk.W, pady=2)
        ttk.Label(form_frame, text="(Comma separated)").grid(row=4, column=2, sticky=tk.W, pady=2)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=5, column=0, sticky=tk.NW, pady=2)
        self.prospect_notes = scrolledtext.ScrolledText(form_frame, width=40, height=5)
        self.prospect_notes.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # Save button
        ttk.Button(form_frame, text="Save Prospect", command=self.save_prospect).grid(row=6, column=1, sticky=tk.E, pady=10)
    
    def create_email_tab(self):
        email_tab = ttk.Frame(self.notebook)
        self.notebook.add(email_tab, text="Email Generator")
        
        # Controls frame
        controls_frame = ttk.Frame(email_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Select Prospect:").pack(side=tk.LEFT, padx=5)
        self.email_prospect_var = tk.StringVar()
        self.email_prospect_combo = ttk.Combobox(controls_frame, textvariable=self.email_prospect_var, state="readonly")
        self.email_prospect_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Generate Email", command=self.generate_email).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Copy to Clipboard", command=self.copy_email).pack(side=tk.LEFT, padx=5)
        
        # Email display
        email_frame = ttk.LabelFrame(email_tab, text="Generated Email")
        email_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.email_text = scrolledtext.ScrolledText(email_frame, width=80, height=25)
        self.email_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_followup_tab(self):
        followup_tab = ttk.Frame(self.notebook)
        self.notebook.add(followup_tab, text="Follow-up Strategy")
        
        # Controls frame
        controls_frame = ttk.Frame(followup_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Select Prospect:").pack(side=tk.LEFT, padx=5)
        self.followup_prospect_var = tk.StringVar()
        self.followup_prospect_combo = ttk.Combobox(controls_frame, textvariable=self.followup_prospect_var, state="readonly")
        self.followup_prospect_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="Days Since Last Contact:").pack(side=tk.LEFT, padx=5)
        self.days_since_contact = tk.StringVar(value="7")
        ttk.Entry(controls_frame, textvariable=self.days_since_contact, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Generate Strategy", command=self.generate_followup).pack(side=tk.LEFT, padx=5)
        
        # Strategy display
        strategy_frame = ttk.LabelFrame(followup_tab, text="Follow-up Strategy")
        strategy_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.strategy_text = scrolledtext.ScrolledText(strategy_frame, width=80, height=25)
        self.strategy_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_objection_tab(self):
        objection_tab = ttk.Frame(self.notebook)
        self.notebook.add(objection_tab, text="Objection Handler")
        
        # Controls frame
        controls_frame = ttk.Frame(objection_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Select Prospect:").pack(side=tk.LEFT, padx=5)
        self.objection_prospect_var = tk.StringVar()
        self.objection_prospect_combo = ttk.Combobox(controls_frame, textvariable=self.objection_prospect_var, state="readonly")
        self.objection_prospect_combo.pack(side=tk.LEFT, padx=5)
        
        # Objection input
        objection_input_frame = ttk.LabelFrame(objection_tab, text="Enter Objection")
        objection_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.objection_input = scrolledtext.ScrolledText(objection_input_frame, width=80, height=5)
        self.objection_input.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(objection_input_frame, text="Analyze Objection", command=self.analyze_objection).pack(pady=5)
        
        # Response display
        response_frame = ttk.LabelFrame(objection_tab, text="Response Strategy")
        response_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, width=80, height=15)
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_proposal_tab(self):
        proposal_tab = ttk.Frame(self.notebook)
        self.notebook.add(proposal_tab, text="Proposal Generator")
        
        # Controls frame
        controls_frame = ttk.Frame(proposal_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Select Prospect:").pack(side=tk.LEFT, padx=5)
        self.proposal_prospect_var = tk.StringVar()
        self.proposal_prospect_combo = ttk.Combobox(controls_frame, textvariable=self.proposal_prospect_var, state="readonly")
        self.proposal_prospect_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Generate Proposal Outline", command=self.generate_proposal).pack(side=tk.LEFT, padx=5)
        
        # Proposal display
        proposal_frame = ttk.LabelFrame(proposal_tab, text="Proposal Outline")
        proposal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.proposal_text = scrolledtext.ScrolledText(proposal_frame, width=80, height=25)
        self.proposal_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_prospect_combos(self):
        prospect_names = list(self.prospects.keys())
        self.email_prospect_combo['values'] = prospect_names
        self.followup_prospect_combo['values'] = prospect_names
        self.objection_prospect_combo['values'] = prospect_names
        self.proposal_prospect_combo['values'] = prospect_names
        
        # Update listbox
        self.prospect_listbox.delete(0, tk.END)
        for name in prospect_names:
            self.prospect_listbox.insert(tk.END, name)
    
    def clear_prospect_form(self):
        self.current_prospect = None
        self.prospect_name.set("")
        self.prospect_company.set("")
        self.prospect_role.set("")
        self.prospect_interests.set("")
        self.prospect_pain_points.set("")
        self.prospect_notes.delete(1.0, tk.END)
    
    def save_prospect(self):
        if not self.sales_agent:
            messagebox.showerror("Error", "Please initialize the API first")
            return
            
        name = self.prospect_name.get()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the prospect")
            return
            
        company = self.prospect_company.get()
        role = self.prospect_role.get()
        interests = [i.strip() for i in self.prospect_interests.get().split(",") if i.strip()]
        pain_points = [p.strip() for p in self.prospect_pain_points.get().split(",") if p.strip()]
        notes = self.prospect_notes.get(1.0, tk.END).strip()
        
        # Update the sales agent
        self.sales_agent.add_prospect_data(
            name=name,
            company=company,
            role=role,
            interests=interests,
            pain_points=pain_points
        )
        
        # Save to our dictionary
        self.prospects[name] = {
            "name": name,
            "company": company,
            "role": role,
            "interests": interests,
            "pain_points": pain_points,
            "notes": notes,
            "last_contact": None,
            "interaction_history": []
        }
        
        # Save to file
        self.save_prospects()
        
        # Update UI
        self.update_prospect_combos()
        messagebox.showinfo("Success", f"Prospect '{name}' saved successfully")
    
    def load_prospect_details(self, event):
        if not self.prospect_listbox.curselection():
            return
            
        index = self.prospect_listbox.curselection()[0]
        name = self.prospect_listbox.get(index)
        prospect = self.prospects.get(name)
        
        if prospect:
            self.current_prospect = name
            self.prospect_name.set(prospect["name"])
            self.prospect_company.set(prospect["company"])
            self.prospect_role.set(prospect["role"])
            self.prospect_interests.set(", ".join(prospect["interests"]))
            self.prospect_pain_points.set(", ".join(prospect["pain_points"]))
            
            self.prospect_notes.delete(1.0, tk.END)
            self.prospect_notes.insert(tk.END, prospect["notes"])
    
    def delete_prospect(self):
        if not self.prospect_listbox.curselection():
            messagebox.showerror("Error", "Please select a prospect to delete")
            return
            
        index = self.prospect_listbox.curselection()[0]
        name = self.prospect_listbox.get(index)
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete prospect '{name}'?"):
            del self.prospects[name]
            self.save_prospects()
            self.update_prospect_combos()
            self.clear_prospect_form()
    
    def generate_email(self):
        if not self.sales_agent:
            messagebox.showerror("Error", "Please initialize the API first")
            return
            
        prospect_name = self.email_prospect_var.get()
        if not prospect_name:
            messagebox.showerror("Error", "Please select a prospect")
            return
            
        prospect = self.prospects.get(prospect_name)
        if not prospect:
            messagebox.showerror("Error", "Selected prospect not found")
            return
            
        # Set the prospect in the sales agent
        self.sales_agent.add_prospect_data(
            name=prospect["name"],
            company=prospect["company"],
            role=prospect["role"],
            interests=prospect["interests"],
            pain_points=prospect["pain_points"]
        )
        
        # Generate email
        try:
            email = self.sales_agent.generate_email()
            self.email_text.delete(1.0, tk.END)
            self.email_text.insert(tk.END, email)
            
            # Log interaction
            self.sales_agent.log_interaction("email", "Generated email")
            self.prospects[prospect_name]["last_contact"] = datetime.now().strftime("%Y-%m-%d")
            self.prospects[prospect_name]["interaction_history"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "email",
                "notes": "Generated email"
            })
            self.save_prospects()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate email: {str(e)}")
    
    def copy_email(self):
        email_text = self.email_text.get(1.0, tk.END).strip()
        if not email_text:
            messagebox.showerror("Error", "No email to copy")
            return
            
        self.root.clipboard_clear()
        self.root.clipboard_append(email_text)
        messagebox.showinfo("Success", "Email copied to clipboard")
    
    def generate_followup(self):
        if not self.sales_agent:
            messagebox.showerror("Error", "Please initialize the API first")
            return
            
        prospect_name = self.followup_prospect_var.get()
        if not prospect_name:
            messagebox.showerror("Error", "Please select a prospect")
            return
            
        prospect = self.prospects.get(prospect_name)
        if not prospect:
            messagebox.showerror("Error", "Selected prospect not found")
            return
            
        try:
            days = int(self.days_since_contact.get())
        except ValueError:
            messagebox.showerror("Error", "Days since contact must be a number")
            return
            
        # Set the prospect in the sales agent
        self.sales_agent.add_prospect_data(
            name=prospect["name"],
            company=prospect["company"],
            role=prospect["role"],
            interests=prospect["interests"],
            pain_points=prospect["pain_points"]
        )
        
        if prospect["last_contact"]:
            self.sales_agent.prospect_data["last_contact"] = prospect["last_contact"]
        
        # Generate follow-up
        try:
            strategy = self.sales_agent.suggest_follow_up(days)
            self.strategy_text.delete(1.0, tk.END)
            self.strategy_text.insert(tk.END, strategy)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate follow-up strategy: {str(e)}")
    
    def analyze_objection(self):
        if not self.sales_agent:
            messagebox.showerror("Error", "Please initialize the API first")
            return
            
        prospect_name = self.objection_prospect_var.get()
        if not prospect_name:
            messagebox.showerror("Error", "Please select a prospect")
            return
            
        prospect = self.prospects.get(prospect_name)
        if not prospect:
            messagebox.showerror("Error", "Selected prospect not found")
            return
            
        objection_text = self.objection_input.get(1.0, tk.END).strip()
        if not objection_text:
            messagebox.showerror("Error", "Please enter an objection")
            return
            
        # Set the prospect in the sales agent
        self.sales_agent.add_prospect_data(
            name=prospect["name"],
            company=prospect["company"],
            role=prospect["role"],
            interests=prospect["interests"],
            pain_points=prospect["pain_points"]
        )
        
        # Analyze objection
        try:
            analysis = self.sales_agent.analyze_objection(objection_text)
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, analysis)
            
            # Log interaction
            self.sales_agent.log_interaction("objection", f"Handled objection: {objection_text}")
            self.prospects[prospect_name]["interaction_history"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "objection",
                "notes": f"Handled objection: {objection_text}"
            })
            self.save_prospects()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze objection: {str(e)}")
    
    def generate_proposal(self):
        if not self.sales_agent:
            messagebox.showerror("Error", "Please initialize the API first")
            return
            
        prospect_name = self.proposal_prospect_var.get()
        if not prospect_name:
            messagebox.showerror("Error", "Please select a prospect")
            return
            
        prospect = self.prospects.get(prospect_name)
        if not prospect:
            messagebox.showerror("Error", "Selected prospect not found")
            return
            
        # Set the prospect in the sales agent
        self.sales_agent.add_prospect_data(
            name=prospect["name"],
            company=prospect["company"],
            role=prospect["role"],
            interests=prospect["interests"],
            pain_points=prospect["pain_points"]
        )
        
        # Generate proposal
        try:
            proposal = self.sales_agent.create_proposal_outline()
            self.proposal_text.delete(1.0, tk.END)
            self.proposal_text.insert(tk.END, proposal)
            
            # Log interaction
            self.sales_agent.log_interaction("proposal", "Generated proposal outline")
            self.prospects[prospect_name]["interaction_history"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "proposal",
                "notes": "Generated proposal outline"
            })
            self.save_prospects()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate proposal: {str(e)}")
    
    def save_prospects(self):
        try:
            with open("prospects.json", "w") as f:
                json.dump(self.prospects, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save prospects: {str(e)}")
    
    def load_prospects(self):
        try:
            if os.path.exists("prospects.json"):
                with open("prospects.json", "r") as f:
                    self.prospects = json.load(f)
                self.update_prospect_combos()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load prospects: {str(e)}")

class SalesAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.conversation_history = []
        self.prospect_data = {}
        
    def add_prospect_data(self, name, company, role, interests=None, pain_points=None):
        """Store information about a sales prospect"""
        self.prospect_data = {
            "name": name,
            "company": company,
            "role": role,
            "interests": interests or [],
            "pain_points": pain_points or [],
            "last_contact": None,
            "interaction_history": []
        }
        
    def log_interaction(self, interaction_type, notes):
        """Record an interaction with the prospect"""
        interaction = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": interaction_type,
            "notes": notes
        }
        self.prospect_data["last_contact"] = datetime.now().strftime("%Y-%m-%d")
        self.prospect_data["interaction_history"].append(interaction)
        
    def generate_email(self):
        """Generate a personalized email for the prospect"""
        if not self.prospect_data:
            return "Please add prospect data first."
            
        prompt = f"""
        Generate a personalized sales email for the following prospect:
        Name: {self.prospect_data['name']}
        Company: {self.prospect_data['company']}
        Role: {self.prospect_data['role']}
        Interests: {', '.join(self.prospect_data['interests'])}
        Pain points: {', '.join(self.prospect_data['pain_points'])}
        
        The email should be:
        1. Professional but conversational
        2. Brief (100-150 words)
        3. Reference their pain points and interests
        4. Include a clear call to action for a meeting
        5. Avoid generic sales language
        """
        
        response = self.model.generate_content(prompt)
        return response.text
        
    def suggest_follow_up(self, days_since_contact):
        """Suggest a follow-up strategy based on time since last contact"""
        prompt = f"""
        Suggest a follow-up strategy for a prospect who hasn't responded in {days_since_contact} days.
        Prospect info:
        Name: {self.prospect_data['name']}
        Company: {self.prospect_data['company']}
        Role: {self.prospect_data['role']}
        Last contact: {self.prospect_data['last_contact'] or 'None'}
        
        Provide:
        1. A suggested follow-up channel (email, call, LinkedIn)
        2. A brief message template
        3. Timing recommendation
        """
        
        response = self.model.generate_content(prompt)
        return response.text
        
    def analyze_objection(self, objection_text):
        """Analyze a sales objection and suggest responses"""
        prompt = f"""
        Analyze this sales objection and provide effective responses:
        
        Prospect: {self.prospect_data['name']} from {self.prospect_data['company']}
        Objection: "{objection_text}"
        
        Provide:
        1. Analysis of the underlying concern
        2. 2-3 effective responses that address the concern
        3. A follow-up question to better understand their needs
        """
        
        response = self.model.generate_content(prompt)
        return response.text
        
    def create_proposal_outline(self):
        """Generate a proposal outline tailored to the prospect"""
        prompt = f"""
        Create a sales proposal outline for:
        
        Prospect: {self.prospect_data['name']}
        Company: {self.prospect_data['company']}
        Role: {self.prospect_data['role']}
        Pain points: {', '.join(self.prospect_data['pain_points'])}
        
        Include:
        1. Executive summary approach
        2. Key sections to include
        3. Recommended metrics/ROI to highlight
        4. Suggested case studies or social proof
        """
        
        response = self.model.generate_content(prompt)
        return response.text

if __name__ == "__main__":
    root = tk.Tk()
    app = SalesAgentGUI(root)
    root.mainloop()