#!/usr/bin/env python3
"""
Program Configuration Editor for SEP QP Generator:
- Edit existing program requirements
- Create new programs
- Validate configurations
- Export configurations
"""

import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ProgramConfigEditor:
    """Editor for SEP program configurations"""
    
    def __init__(self, config_file="sep_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found!")
            return {}
            
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
            
    def list_programs(self) -> None:
        """List all available programs"""
        print("\n📋 Available Programs:")
        print("-" * 50)
        
        for key, program in self.config.get("programs", {}).items():
            print(f"🔑 Key: {key}")
            print(f"   Name: {program.get('name', 'N/A')}")
            print(f"   Description: {program.get('description', 'N/A')}")
            print(f"   Min Acres: {program.get('requirements', {}).get('min_acres', 'N/A')}")
            print(f"   Max Slope: {program.get('requirements', {}).get('max_slope_pct', 'N/A')}%")
            print()
            
    def show_program_details(self, program_key: str) -> None:
        """Show detailed information about a specific program"""
        if program_key not in self.config.get("programs", {}):
            print(f"❌ Program '{program_key}' not found!")
            return
            
        program = self.config["programs"][program_key]
        
        print(f"\n📊 Program Details: {program_key}")
        print("=" * 60)
        print(f"Name: {program.get('name', 'N/A')}")
        print(f"Description: {program.get('description', 'N/A')}")
        
        print("\n📋 Requirements:")
        reqs = program.get("requirements", {})
        print(f"  • Min Acres: {reqs.get('min_acres', 'N/A')}")
        print(f"  • Max Acres: {reqs.get('max_acres', 'N/A')}")
        print(f"  • Max Slope: {reqs.get('max_slope_pct', 'N/A')}%")
        print(f"  • Max Road Distance: {reqs.get('max_dist_to_road_miles', 'N/A')} miles")
        print(f"  • Allowed Soils: {', '.join(reqs.get('allowed_soil_orders', []))}")
        print(f"  • Excluded Soils: {', '.join(reqs.get('excluded_soil_orders', []))}")
        print(f"  • Allowed Land Use: {', '.join(reqs.get('allowed_landuse', []))}")
        print(f"  • Min Organic Matter: {reqs.get('min_organic_matter', 'N/A')}%")
        print(f"  • Max Erodibility: {reqs.get('max_erodibility', 'N/A')}")
        print(f"  • Required Practices: {', '.join(reqs.get('required_practices', []))}")
        print(f"  • Stacking Allowed: {reqs.get('stacking_allowed', 'N/A')}")
        
        print("\n🏆 Scoring Weights:")
        scoring = program.get("scoring", {})
        for category, weight in scoring.items():
            print(f"  • {category.replace('_', ' ').title()}: {weight}")
            
        print("\n🚫 County Restrictions:")
        restrictions = reqs.get("county_restrictions", {})
        for county, status in restrictions.items():
            print(f"  • {county}: {status}")
            
    def edit_program_requirement(self, program_key: str, requirement: str, value: Any) -> bool:
        """Edit a specific program requirement"""
        if program_key not in self.config.get("programs", {}):
            print(f"❌ Program '{program_key}' not found!")
            return False
            
        program = self.config["programs"][program_key]
        requirements = program.get("requirements", {})
        
        # Handle nested requirements
        if "." in requirement:
            parts = requirement.split(".")
            if len(parts) == 2:
                category, field = parts
                if category in requirements:
                    requirements[category][field] = value
                else:
                    requirements[category] = {field: value}
            else:
                print("❌ Invalid requirement format. Use 'category.field' or 'field'")
                return False
        else:
            requirements[requirement] = value
            
        print(f"✅ Updated {program_key}.{requirement} = {value}")
        return True
        
    def create_new_program(self, program_key: str, name: str, description: str) -> bool:
        """Create a new program"""
        if program_key in self.config.get("programs", {}):
            print(f"❌ Program '{program_key}' already exists!")
            return False
            
        # Create default program structure
        new_program = {
            "name": name,
            "description": description,
            "requirements": {
                "min_acres": 10,
                "max_acres": 1000,
                "max_slope_pct": 15,
                "max_dist_to_road_miles": 1.0,
                "allowed_soil_orders": ["Alfisols", "Mollisols", "Entisols"],
                "excluded_soil_orders": ["Histosols"],
                "allowed_landuse": ["farmland", "farmyard"],
                "min_organic_matter": 1.0,
                "max_erodibility": 0.4,
                "required_practices": [],
                "stacking_allowed": True,
                "county_restrictions": {}
            },
            "scoring": {
                "acres": 25,
                "soil_health": 25,
                "erosion_risk": 25,
                "access": 25
            }
        }
        
        self.config["programs"][program_key] = new_program
        print(f"✅ Created new program: {program_key} - {name}")
        return True
        
    def delete_program(self, program_key: str) -> bool:
        """Delete a program"""
        if program_key not in self.config.get("programs", {}):
            print(f"❌ Program '{program_key}' not found!")
            return False
            
        program_name = self.config["programs"][program_key]["name"]
        del self.config["programs"][program_key]
        print(f"✅ Deleted program: {program_key} - {program_name}")
        return True
        
    def validate_program(self, program_key: str) -> bool:
        """Validate a program configuration"""
        if program_key not in self.config.get("programs", {}):
            print(f"❌ Program '{program_key}' not found!")
            return False
            
        program = self.config["programs"][program_key]
        requirements = program.get("requirements", {})
        scoring = program.get("scoring", {})
        
        errors = []
        
        # Check required fields
        required_fields = ["name", "description", "requirements", "scoring"]
        for field in required_fields:
            if field not in program:
                errors.append(f"Missing required field: {field}")
                
        # Check requirements
        if "min_acres" in requirements and "max_acres" in requirements:
            if requirements["min_acres"] > requirements["max_acres"]:
                errors.append("min_acres cannot be greater than max_acres")
                
        # Check scoring weights
        total_score = sum(scoring.values())
        if total_score != 100:
            errors.append(f"Scoring weights must sum to 100 (current: {total_score})")
            
        if errors:
            print(f"❌ Validation errors for program '{program_key}':")
            for error in errors:
                print(f"  • {error}")
            return False
        else:
            print(f"✅ Program '{program_key}' is valid!")
            return True
            
    def export_program(self, program_key: str, output_file: str = None) -> bool:
        """Export a program configuration to a separate file"""
        if program_key not in self.config.get("programs", {}):
            print(f"❌ Program '{program_key}' not found!")
            return False
            
        if output_file is None:
            output_file = f"{program_key}_config.json"
            
        try:
            program_config = {
                "program": self.config["programs"][program_key],
                "exported": True,
                "source": self.config_file
            }
            
            with open(output_file, 'w') as f:
                json.dump(program_config, f, indent=2)
                
            print(f"✅ Exported program '{program_key}' to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting program: {e}")
            return False
            
    def import_program(self, import_file: str, program_key: str = None) -> bool:
        """Import a program configuration from a file"""
        try:
            with open(import_file, 'r') as f:
                import_data = json.load(f)
                
            if "program" not in import_data:
                print("❌ Invalid import file format")
                return False
                
            program = import_data["program"]
            
            if program_key is None:
                program_key = program.get("name", "").lower().replace(" ", "_")
                
            if program_key in self.config.get("programs", {}):
                print(f"⚠️  Program '{program_key}' already exists. Overwriting...")
                
            self.config["programs"][program_key] = program
            print(f"✅ Imported program '{program_key}' from {import_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error importing program: {e}")
            return False

def interactive_editor():
    """Interactive program configuration editor"""
    editor = ProgramConfigEditor()
    
    if not editor.config:
        print("❌ Failed to load configuration. Exiting.")
        return
        
    while True:
        print("\n" + "="*60)
        print("🔧 SEP Program Configuration Editor")
        print("="*60)
        print("1. List all programs")
        print("2. Show program details")
        print("3. Edit program requirement")
        print("4. Create new program")
        print("5. Delete program")
        print("6. Validate program")
        print("7. Export program")
        print("8. Import program")
        print("9. Save configuration")
        print("0. Exit")
        
        choice = input("\nSelect option (0-9): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
            
        elif choice == "1":
            editor.list_programs()
            
        elif choice == "2":
            program_key = input("Enter program key: ").strip()
            editor.show_program_details(program_key)
            
        elif choice == "3":
            program_key = input("Enter program key: ").strip()
            requirement = input("Enter requirement (e.g., 'min_acres' or 'county_restrictions.MCLEAN'): ").strip()
            value_input = input("Enter new value: ").strip()
            
            # Try to convert value to appropriate type
            try:
                if value_input.lower() in ['true', 'false']:
                    value = value_input.lower() == 'true'
                elif value_input.isdigit():
                    value = int(value_input)
                elif value_input.replace('.', '').isdigit():
                    value = float(value_input)
                elif value_input.startswith('[') and value_input.endswith(']'):
                    # Handle list input
                    value = [item.strip().strip('"\'') for item in value_input[1:-1].split(',')]
                else:
                    value = value_input
                    
                editor.edit_program_requirement(program_key, requirement, value)
            except Exception as e:
                print(f"❌ Error parsing value: {e}")
                
        elif choice == "4":
            program_key = input("Enter program key: ").strip()
            name = input("Enter program name: ").strip()
            description = input("Enter program description: ").strip()
            editor.create_new_program(program_key, name, description)
            
        elif choice == "5":
            program_key = input("Enter program key: ").strip()
            confirm = input(f"Are you sure you want to delete '{program_key}'? (y/N): ").strip().lower()
            if confirm == 'y':
                editor.delete_program(program_key)
                
        elif choice == "6":
            program_key = input("Enter program key: ").strip()
            editor.validate_program(program_key)
            
        elif choice == "7":
            program_key = input("Enter program key: ").strip()
            output_file = input("Enter output file (or press Enter for default): ").strip()
            if not output_file:
                output_file = None
            editor.export_program(program_key, output_file)
            
        elif choice == "8":
            import_file = input("Enter import file path: ").strip()
            program_key = input("Enter program key (or press Enter for auto): ").strip()
            if not program_key:
                program_key = None
            editor.import_program(import_file, program_key)
            
        elif choice == "9":
            if editor.save_config():
                print("✅ Configuration saved successfully!")
            else:
                print("❌ Failed to save configuration!")
                
        else:
            print("❌ Invalid option. Please try again.")

def main():
    """Main function"""
    print("🔧 SEP Program Configuration Editor")
    print("=" * 60)
    
    # Check if configuration file exists
    if not os.path.exists("sep_config.json"):
        print("❌ Configuration file 'sep_config.json' not found!")
        print("💡 Please run the main SEP QP Generator first to create the configuration.")
        return
        
    # Start interactive editor
    interactive_editor()

if __name__ == "__main__":
    main() 