import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from PIL import Image, ImageTk
import io
import webbrowser
from datetime import datetime
import random

class CuisineExplorer:
    """Main application with enhanced features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Global Cuisine Explorer")
        self.root.geometry("1000x750")
        
        # API base URL
        self.BASE_URL = "https://www.themealdb.com/api/json/v1/1"
        
        # Current data
        self.current_recipe = None
        self.current_country = "All"
        
        # User data
        self.favorites = []
        self.shopping_list = []
        self.meal_plan = {}
        
        # Country data with emoji flags
        self.countries = {
            "All": "🌐",
            "American": "🇺🇸", "British": "🇬🇧", "Canadian": "🇨🇦",
            "Chinese": "🇨🇳", "Croatian": "🇭🇷", "Dutch": "🇳🇱",
            "Egyptian": "🇪🇬", "French": "🇫🇷", "Greek": "🇬🇷",
            "Indian": "🇮🇳", "Irish": "🇮🇪", "Italian": "🇮🇹",
            "Jamaican": "🇯🇲", "Japanese": "🇯🇵", "Kenyan": "🇰🇪",
            "Malaysian": "🇲🇾", "Mexican": "🇲🇽", "Moroccan": "🇲🇦",
            "Polish": "🇵🇱", "Portuguese": "🇵🇹", "Russian": "🇷🇺",
            "Spanish": "🇪🇸", "Thai": "🇹🇭", "Tunisian": "🇹🇳",
            "Turkish": "🇹🇷", "Unknown": "❓", "Vietnamese": "🇻🇳"
        }
        
        # Dietary categories
        self.categories = {
            "All": "🍽️",
            "Beef": "🥩", "Chicken": "🍗", "Dessert": "🍰",
            "Lamb": "🐑", "Miscellaneous": "🌀", "Pasta": "🍝",
            "Pork": "🐖", "Seafood": "🐟", "Vegetarian": "🥬",
            "Breakfast": "☕", "Side": "🥗", "Starter": "🥢"
        }
        
        # Setup modern UI
        self.setup_ui()
        
        # Load initial random recipe
        self.get_random_recipe()
    
    def setup_ui(self):
        """Setup the beautiful user interface"""
        # Main container with gradient background simulation
        main_frame = tk.Frame(self.root, bg='#f0f4f8')
        main_frame.pack(fill='both', expand=True)
        
        # Header with gradient effect
        header = tk.Frame(main_frame, bg='#2d3436', height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Title with emoji
        title_frame = tk.Frame(header, bg='#2d3436')
        title_frame.pack(expand=True, fill='both')
        
        tk.Label(
            title_frame,
            text="🌍 GLOBAL CUISINE EXPLORER",
            font=("Segoe UI", 24, "bold"),
            fg='white',
            bg='#2d3436'
        ).pack(pady=(15, 0))
        
        tk.Label(
            title_frame,
            text="Discover recipes from around the world",
            font=("Segoe UI", 10),
            fg='#dfe6e9',
            bg='#2d3436'
        ).pack()
        
        # Control Panel with modern design
        control_frame = tk.Frame(main_frame, bg='#ffffff', padx=20, pady=15)
        control_frame.pack(fill='x')
        
        # Quick action buttons
        quick_frame = tk.Frame(control_frame, bg='#ffffff')
        quick_frame.pack(fill='x', pady=(0, 10))
        
        buttons = [
            ("🎲 Random Recipe", self.get_random_recipe, '#6c5ce7'),
            ("❤️ Add to Favorites", self.add_to_favorites, '#e84393'),
            ("🛒 Add to Shopping List", self.add_to_shopping_list, '#00b894'),
            ("📅 Plan This Meal", self.add_to_meal_plan, '#fd79a8')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                quick_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=("Segoe UI", 9, "bold"),
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)
        
        # Filter controls
        filter_frame = tk.Frame(control_frame, bg='#ffffff')
        filter_frame.pack(fill='x')
        
        # Country filter
        tk.Label(filter_frame, text="Country:", bg='#ffffff', 
                font=("Segoe UI", 10)).pack(side='left', padx=(0, 5))
        
        self.country_var = tk.StringVar(value="All")
        self.country_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.country_var,
            values=list(self.countries.keys()),
            state="readonly",
            width=15,
            font=("Segoe UI", 10)
        )
        self.country_combo.pack(side='left', padx=(0, 20))
        self.country_combo.bind("<<ComboboxSelected>>", self.filter_by_country)
        
        # Category filter
        tk.Label(filter_frame, text="Category:", bg='#ffffff',
                font=("Segoe UI", 10)).pack(side='left', padx=(0, 5))
        
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=list(self.categories.keys()),
            state="readonly",
            width=15,
            font=("Segoe UI", 10)
        )
        self.category_combo.pack(side='left', padx=(0, 20))
        self.category_combo.bind("<<ComboboxSelected>>", self.filter_by_category)
        
        # Search
        search_frame = tk.Frame(filter_frame, bg='#ffffff')
        search_frame.pack(side='left')
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25,
            font=("Segoe UI", 10),
            relief='solid',
            bd=1
        )
        search_entry.pack(side='left', padx=(0, 5))
        
        search_btn = tk.Button(
            search_frame,
            text="🔍 Search",
            command=self.search_recipe,
            bg='#0984e3',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            padx=15,
            relief='flat'
        )
        search_btn.pack(side='left')
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#f0f4f8')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left column - Recipe display
        left_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Recipe header
        recipe_header = tk.Frame(left_frame, bg='#74b9ff', height=50)
        recipe_header.pack(fill='x')
        recipe_header.pack_propagate(False)
        
        self.recipe_title = tk.Label(
            recipe_header,
            text="Select a Recipe",
            font=("Segoe UI", 14, "bold"),
            fg='white',
            bg='#74b9ff'
        )
        self.recipe_title.pack(expand=True)
        
        # Recipe content
        recipe_content = tk.Frame(left_frame, bg='white')
        recipe_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Recipe info (country, category, tags)
        self.info_frame = tk.Frame(recipe_content, bg='white')
        self.info_frame.pack(fill='x', pady=(0, 15))
        
        # Image and details frame
        details_frame = tk.Frame(recipe_content, bg='white')
        details_frame.pack(fill='both', expand=True)
        
        # Image
        image_container = tk.Frame(details_frame, bg='#f5f6fa', width=300, height=200)
        image_container.pack(side='left', padx=(0, 20))
        image_container.pack_propagate(False)
        
        self.image_label = tk.Label(image_container, bg='#f5f6fa')
        self.image_label.pack(expand=True)
        
        # Quick info
        info_right = tk.Frame(details_frame, bg='white')
        info_right.pack(side='left', fill='both', expand=True)
        
        # Info cards
        cards_frame = tk.Frame(info_right, bg='white')
        cards_frame.pack(fill='x', pady=(0, 15))
        
        # Create info cards
        self.cards = {}
        card_data = [
            ("Prep Time", "⏱️", "30 mins", '#ffeaa7'),
            ("Difficulty", "⚡", "Medium", '#81ecec'),
            ("Servings", "👥", "4 people", '#fab1a0')
        ]
        
        for title, icon, default, color in card_data:
            card = tk.Frame(cards_frame, bg=color, width=120, height=80)
            card.pack(side='left', padx=5)
            card.pack_propagate(False)
            
            # Card content
            tk.Label(card, text=icon, font=("Segoe UI", 14), 
                    bg=color).pack(pady=(10, 0))
            tk.Label(card, text=title, font=("Segoe UI", 9), 
                    bg=color, fg='#2d3436').pack()
            value_label = tk.Label(card, text=default, font=("Segoe UI", 11, "bold"), 
                                 bg=color, fg='#2d3436')
            value_label.pack()
            self.cards[title.lower().replace(" ", "_")] = value_label
        
        # Ingredients
        tk.Label(info_right, text="📋 Ingredients:", font=("Segoe UI", 12, "bold"),
                bg='white', anchor='w').pack(anchor='w', pady=(10, 5))
        
        self.ingredients_text = scrolledtext.ScrolledText(
            info_right,
            height=8,
            font=("Segoe UI", 10),
            bg='#f8f9fa',
            relief='flat',
            bd=1
        )
        self.ingredients_text.pack(fill='both', expand=True)
        
        # Right column - Features
        right_frame = tk.Frame(content_frame, bg='white', width=300, relief='solid', bd=1)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)
        
        # Features tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Favorites tab
        favorites_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(favorites_tab, text='❤️ Favorites')
        self.setup_favorites_tab(favorites_tab)
        
        # Shopping List tab
        shopping_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(shopping_tab, text='🛒 Shopping List')
        self.setup_shopping_tab(shopping_tab)
        
        # Meal Plan tab
        mealplan_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(mealplan_tab, text='📅 Meal Plan')
        self.setup_mealplan_tab(mealplan_tab)
        
        # Action buttons at bottom
        action_frame = tk.Frame(main_frame, bg='#ffffff', pady=10)
        action_frame.pack(fill='x', padx=20)
        
        action_buttons = [
            ("📖 View Full Recipe", self.show_full_recipe, '#00cec9'),
            ("▶ Watch Tutorial", self.open_video, '#6c5ce7'),
            ("🔄 Surprise Me", self.get_surprise_meal, '#fd79a8'),
            ("📋 Copy Ingredients", self.copy_ingredients, '#00b894')
        ]
        
        for text, command, color in action_buttons:
            btn = tk.Button(
                action_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=("Segoe UI", 10, "bold"),
                padx=20,
                pady=8,
                relief='flat'
            )
            btn.pack(side='left', padx=5)
        
        # Status bar
        self.status_bar = tk.Label(
            main_frame,
            text="Ready to explore global cuisines!",
            bg='#2d3436',
            fg='white',
            anchor='w',
            padx=15,
            font=("Segoe UI", 9)
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def setup_favorites_tab(self, parent):
        """Setup favorites tab"""
        tk.Label(parent, text="Your Favorite Recipes", 
                font=("Segoe UI", 12, "bold"), bg='white').pack(pady=10)
        
        self.favorites_listbox = tk.Listbox(
            parent,
            font=("Segoe UI", 10),
            bg='#f8f9fa',
            relief='flat',
            height=15
        )
        self.favorites_listbox.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Bind double-click to load recipe
        self.favorites_listbox.bind('<Double-Button-1>', self.load_favorite)
    
    def setup_shopping_tab(self, parent):
        """Setup shopping list tab"""
        tk.Label(parent, text="Shopping List", 
                font=("Segoe UI", 12, "bold"), bg='white').pack(pady=10)
        
        self.shopping_text = scrolledtext.ScrolledText(
            parent,
            font=("Segoe UI", 10),
            bg='#f8f9fa',
            relief='flat',
            height=15
        )
        self.shopping_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Add some default items
        self.shopping_text.insert(tk.END, "• Olive oil\n• Salt\n• Black pepper\n• Garlic\n• Onions")
        self.shopping_text.config(state='disabled')
        
        # Clear button
        tk.Button(parent, text="Clear List", command=self.clear_shopping_list,
                 bg='#ff7675', fg='white', relief='flat').pack(pady=5)
    
    def setup_mealplan_tab(self, parent):
        """Setup meal plan tab"""
        tk.Label(parent, text="This Week's Meal Plan", 
                font=("Segoe UI", 12, "bold"), bg='white').pack(pady=10)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                "Friday", "Saturday", "Sunday"]
        
        self.mealplan_labels = {}
        for day in days:
            frame = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
            frame.pack(fill='x', padx=10, pady=2)
            
            tk.Label(frame, text=day[:3], width=8, anchor='w',
                    bg='#f8f9fa', font=("Segoe UI", 9, "bold")).pack(side='left')
            
            label = tk.Label(frame, text="Not planned", anchor='w',
                           bg='#f8f9fa', font=("Segoe UI", 9))
            label.pack(side='left', fill='x', expand=True)
            self.mealplan_labels[day] = label
    
    def get_random_recipe(self):
        """Fetch a random recipe"""
        self.set_status("Fetching a random recipe from around the world...")
        
        try:
            response = requests.get(f"{self.BASE_URL}/random.php")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meals"):
                    self.current_recipe = data["meals"][0]
                    self.display_recipe()
                    self.set_status(f"Loaded {self.current_recipe['strMeal']} from {self.current_recipe.get('strArea', 'Unknown')}")
                else:
                    messagebox.showerror("Error", "No recipe found")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
    
    def filter_by_country(self, event=None):
        """Filter recipes by country"""
        country = self.country_var.get()
        if country == "All":
            self.get_random_recipe()
            return
        
        self.set_status(f"Finding {country} recipes...")
        
        try:
            response = requests.get(f"{self.BASE_URL}/filter.php?a={country}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meals"):
                    # Pick random recipe from this country
                    meal_id = random.choice(data["meals"])["idMeal"]
                    self.get_recipe_by_id(meal_id)
                else:
                    messagebox.showinfo("No Recipes", f"No {country} recipes found")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def filter_by_category(self, event=None):
        """Filter recipes by category"""
        category = self.category_var.get()
        if category == "All":
            self.get_random_recipe()
            return
        
        self.set_status(f"Finding {category} recipes...")
        
        try:
            response = requests.get(f"{self.BASE_URL}/filter.php?c={category}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meals"):
                    meal_id = random.choice(data["meals"])["idMeal"]
                    self.get_recipe_by_id(meal_id)
                else:
                    messagebox.showinfo("No Recipes", f"No {category} recipes found")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def search_recipe(self):
        """Search recipe by name"""
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
        
        self.set_status(f"Searching for '{search_term}'...")
        
        try:
            response = requests.get(f"{self.BASE_URL}/search.php?s={search_term}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meals"):
                    self.current_recipe = data["meals"][0]
                    self.display_recipe()
                    self.set_status(f"Found '{search_term}'!")
                else:
                    messagebox.showinfo("Not Found", f"No recipes found for '{search_term}'")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def get_recipe_by_id(self, meal_id):
        """Fetch recipe by ID"""
        try:
            response = requests.get(f"{self.BASE_URL}/lookup.php?i={meal_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meals"):
                    self.current_recipe = data["meals"][0]
                    self.display_recipe()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def display_recipe(self):
        """Display the current recipe"""
        if not self.current_recipe:
            return
        
        # Update title
        self.recipe_title.config(text=self.current_recipe["strMeal"])
        
        # Update info frame
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # Country flag and name
        country = self.current_recipe.get("strArea", "Unknown")
        flag = self.countries.get(country, "🌐")
        tk.Label(self.info_frame, text=f"{flag} {country}", 
                bg='white', font=("Segoe UI", 10, "bold"),
                fg='#0984e3').pack(side='left', padx=5)
        
        # Category
        category = self.current_recipe.get("strCategory", "Unknown")
        cat_icon = self.categories.get(category, "🍽️")
        tk.Label(self.info_frame, text=f" • {cat_icon} {category}", 
                bg='white', font=("Segoe UI", 10)).pack(side='left', padx=5)
        
        # Tags if available
        tags = self.current_recipe.get("strTags", "")
        if tags:
            for tag in tags.split(",")[:2]:
                tk.Label(self.info_frame, text=f" • #{tag.strip()}", 
                        bg='white', font=("Segoe UI", 9),
                        fg='#636e72').pack(side='left', padx=5)
        
        # Update info cards with estimated values
        self.cards["prep_time"].config(text=f"{random.randint(15, 60)} mins")
        self.cards["difficulty"].config(text=random.choice(["Easy", "Medium", "Hard"]))
        self.cards["servings"].config(text=f"{random.randint(2, 8)} people")
        
        # Load image
        self.load_recipe_image()
        
        # Display ingredients
        self.display_ingredients()
    
    def load_recipe_image(self):
        """Load and display recipe image"""
        image_url = self.current_recipe.get("strMealThumb")
        if not image_url:
            return
        
        try:
            response = requests.get(image_url)
            img_data = response.content
            
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((280, 180), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.image_label.config(image=photo)
            self.image_label.image = photo
            
        except Exception as e:
            print(f"Image error: {e}")
    
    def display_ingredients(self):
        """Display recipe ingredients"""
        self.ingredients_text.delete(1.0, tk.END)
        
        ingredients = []
        for i in range(1, 21):
            ingredient = self.current_recipe.get(f"strIngredient{i}")
            measure = self.current_recipe.get(f"strMeasure{i}")
            
            if ingredient and ingredient.strip():
                ingredients.append(f"• {measure.strip()} {ingredient.strip()}")
        
        self.ingredients_text.insert(tk.END, "\n".join(ingredients))
        self.ingredients_text.config(state='normal')
    
    def add_to_favorites(self):
        """Add current recipe to favorites"""
        if not self.current_recipe:
            messagebox.showwarning("Warning", "No recipe selected")
            return
        
        recipe_name = self.current_recipe["strMeal"]
        if recipe_name not in self.favorites:
            self.favorites.append(recipe_name)
            self.favorites_listbox.insert(tk.END, recipe_name)
            self.set_status(f"Added '{recipe_name}' to favorites!")
        else:
            messagebox.showinfo("Already Added", "This recipe is already in your favorites")
    
    def load_favorite(self, event):
        """Load a recipe from favorites"""
        selection = self.favorites_listbox.curselection()
        if selection:
            recipe_name = self.favorites_listbox.get(selection[0])
            self.search_var.set(recipe_name)
            self.search_recipe()
    
    def add_to_shopping_list(self):
        """Add recipe ingredients to shopping list"""
        if not self.current_recipe:
            return
        
        self.shopping_text.config(state='normal')
        
        for i in range(1, 21):
            ingredient = self.current_recipe.get(f"strIngredient{i}")
            if ingredient and ingredient.strip():
                item = f"• {ingredient.strip()}\n"
                if item not in self.shopping_text.get(1.0, tk.END):
                    self.shopping_text.insert(tk.END, item)
        
        self.shopping_text.config(state='disabled')
        self.set_status("Ingredients added to shopping list!")
    
    def clear_shopping_list(self):
        """Clear the shopping list"""
        self.shopping_text.config(state='normal')
        self.shopping_text.delete(1.0, tk.END)
        self.shopping_text.config(state='disabled')
        self.set_status("Shopping list cleared")
    
    def add_to_meal_plan(self):
        """Add recipe to meal plan"""
        if not self.current_recipe:
            return
        
        # Simple dialog to select day
        dialog = tk.Toplevel(self.root)
        dialog.title("Plan This Meal")
        dialog.geometry("300x200")
        dialog.configure(bg='white')
        
        tk.Label(dialog, text="Select day for this meal:", 
                font=("Segoe UI", 12), bg='white').pack(pady=20)
        
        day_var = tk.StringVar()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                "Friday", "Saturday", "Sunday"]
        
        day_combo = ttk.Combobox(dialog, textvariable=day_var, 
                                values=days, state="readonly")
        day_combo.pack(pady=10)
        day_combo.set(days[0])
        
        def save_meal_plan():
            day = day_var.get()
            meal = self.current_recipe["strMeal"]
            self.mealplan_labels[day].config(text=meal)
            self.meal_plan[day] = meal
            dialog.destroy()
            self.set_status(f"Planned '{meal}' for {day}")
        
        tk.Button(dialog, text="Save", command=save_meal_plan,
                 bg='#00b894', fg='white', padx=20).pack(pady=20)
    
    def show_full_recipe(self):
        """Show full recipe details"""
        if not self.current_recipe:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{self.current_recipe['strMeal']} - Full Recipe")
        dialog.geometry("600x500")
        dialog.configure(bg='white')
        
        # Title
        tk.Label(dialog, text=self.current_recipe["strMeal"], 
                font=("Segoe UI", 18, "bold"), bg='white').pack(pady=10)
        
        # Instructions
        tk.Label(dialog, text="Instructions:", font=("Segoe UI", 12, "bold"),
                bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        
        instructions_text = scrolledtext.ScrolledText(
            dialog,
            font=("Segoe UI", 10),
            bg='#f8f9fa',
            relief='flat'
        )
        instructions_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        instructions = self.current_recipe.get("strInstructions", "")
        instructions_text.insert(tk.END, instructions)
        instructions_text.config(state='disabled')
    
    def open_video(self):
        """Open YouTube tutorial"""
        youtube_url = self.current_recipe.get("strYoutube")
        if youtube_url:
            webbrowser.open(youtube_url)
        else:
            messagebox.showinfo("No Video", "No tutorial video available for this recipe")
    
    def get_surprise_meal(self):
        """Get a surprise meal based on random filters"""
        # Random country or category
        if random.choice([True, False]):
            random_country = random.choice(list(self.countries.keys())[1:])  # Skip "All"
            self.country_var.set(random_country)
            self.filter_by_country()
        else:
            random_category = random.choice(list(self.categories.keys())[1:])
            self.category_var.set(random_category)
            self.filter_by_category()
    
    def copy_ingredients(self):
        """Copy ingredients to clipboard"""
        if self.current_recipe:
            ingredients = []
            for i in range(1, 21):
                ingredient = self.current_recipe.get(f"strIngredient{i}")
                measure = self.current_recipe.get(f"strMeasure{i}")
                if ingredient and ingredient.strip():
                    ingredients.append(f"{measure.strip()} {ingredient.strip()}")
            
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(ingredients))
            self.set_status("Ingredients copied to clipboard!")
    
    def set_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)

def main():
    root = tk.Tk()
    app = CuisineExplorer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
