from pypdfium2 import PdfDocument
import sys

def check_pdf(path):
    print(f"Checking PDF: {path}")
    try:
        pdf = PdfDocument(path)
        print(f"Number of pages: {len(pdf)}")
        
        # Try to read first page
        page = pdf[0]
        width, height = page.get_size()
        print(f"Page size: {width} x {height}")
        
        # Try to extract text
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        print("\nFirst 200 characters of text:")
        print(text[:200])
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_tables.pdf"
    check_pdf(path)