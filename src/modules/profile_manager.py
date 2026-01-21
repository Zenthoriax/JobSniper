import json
import os

PROFILE_PATH = os.path.join("data", "profile.json")

class ProfileManager:
    def __init__(self):
        self.profile_path = PROFILE_PATH
        self.data = self._load_profile()

    def _load_profile(self):
        """Loads profile data or returns a skeleton if missing."""
        if not os.path.exists(self.profile_path):
            print("⚠️ Profile not found. Creating new...")
            return {"name": "", "skills": [], "projects": []}
        
        with open(self.profile_path, 'r') as f:
            return json.load(f)

    def _save_profile(self):
        """Writes current data state to JSON."""
        with open(self.profile_path, 'w') as f:
            json.dump(self.data, f, indent=2)
        print("💾 Profile saved successfully.")

    # --- SKILLS OPERATIONS ---
    def add_skill(self, skill):
        if skill not in self.data["skills"]:
            self.data["skills"].append(skill)
            self._save_profile()
            print(f"✅ Added skill: {skill}")
        else:
            print(f"⚠️ Skill '{skill}' already exists.")

    def remove_skill(self, skill):
        if skill in self.data["skills"]:
            self.data["skills"].remove(skill)
            self._save_profile()
            print(f"🗑️ Removed skill: {skill}")
        else:
            print(f"❌ Skill '{skill}' not found.")

    # --- PROJECT OPERATIONS ---
    def add_project(self, name, tech, description):
        new_project = {
            "name": name,
            "tech": tech,
            "description": description
        }
        self.data["projects"].append(new_project)
        self._save_profile()
        print(f"✅ Added project: {name}")

    def delete_project(self, project_name):
        initial_count = len(self.data["projects"])
        # Filter out the project with the matching name
        self.data["projects"] = [p for p in self.data["projects"] if p["name"].lower() != project_name.lower()]
        
        if len(self.data["projects"]) < initial_count:
            self._save_profile()
            print(f"🗑️ Deleted project: {project_name}")
        else:
            print(f"❌ Project '{project_name}' not found.")

    def list_profile(self):
        """Prints a summary of the current profile."""
        print(f"\n👤 Name: {self.data.get('name', 'N/A')}")
        print(f"📚 Skills ({len(self.data['skills'])}): {', '.join(self.data['skills'])}")
        print(f"🚀 Projects ({len(self.data['projects'])}):")
        for p in self.data['projects']:
            print(f"   - {p['name']} [{p.get('tech', '')}]")