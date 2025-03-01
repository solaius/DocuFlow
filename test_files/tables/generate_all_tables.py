from pathlib import Path
from basic_tables import create_basic_tables_pdf
from moderate_tables import create_moderate_tables_pdf

def generate_all_tables():
    """Generate all table test files"""
    # Ensure output directory exists
    output_dir = Path("test_files")
    output_dir.mkdir(exist_ok=True)
    
    # Generate basic tables
    print("Generating basic tables...")
    create_basic_tables_pdf(str(output_dir / "basic_tables.pdf"))
    
    # Generate moderate tables
    print("Generating moderate tables...")
    create_moderate_tables_pdf(str(output_dir / "moderate_tables.pdf"))
    
    print("All tables generated successfully!")

if __name__ == '__main__':
    generate_all_tables()