import os
import base64
from pathlib import Path
from ollama import chat
from pdf2image import convert_from_path
from io import BytesIO
import fitz  # PyMuPDF for PDF text extraction

# myTigerTrail - UOP Campus Navigation Assistant


def load_map_image():
    """
    Load and encode the campus map PNG image in base64 format for LLM processing.
    
    Returns:
        str: Base64 encoded image data
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    image_path = script_dir / "pacific_map.png"
    
    if not image_path.exists():
        raise FileNotFoundError(f"Campus map image not found at {image_path}")
    
    # Check file size - warn if too large
    file_size = image_path.stat().st_size
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        print(f"⚠️  Warning: Image file is large ({file_size} bytes), this may affect processing")
    #The place where we needed to add the code to check if the file is a valid PNG and warn if not 
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        # Validate it's a PNG file
        if not image_data.startswith(b'\x89PNG'):
            print("⚠️  Warning: File doesn't appear to be a valid PNG")
        
        encoded_data = base64.b64encode(image_data).decode("utf-8")
        return encoded_data
        
    except Exception as e:
        raise Exception(f"Error loading image: {str(e)}")


def extract_pdf_text():
    """
    Extract text content from the campus map PDF for additional context.
    
    Returns:
        str: Extracted text from the PDF
    """
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "Pacific-Stk-CampusMap.pdf"
    
    if not pdf_path.exists():
        return "PDF context not available - proceeding with image analysis only."
    
    try:
        # Open the PDF with PyMuPDF
        doc = fitz.open(str(pdf_path))
        text_content = []
        
        # Extract text from all pages
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                # Clean the text - remove excessive whitespace and non-printable characters
                cleaned_text = ' '.join(text.split())
                if len(cleaned_text) > 10:  # Only include substantial text
                    text_content.append(f"Page {page_num + 1}: {cleaned_text}")
        
        doc.close()
        
        if text_content:
            full_text = "\n\n".join(text_content)
            return full_text
        else:
            return "No text content found in PDF."
            
    except Exception as e:
        return f"Could not extract PDF text: {str(e)}"


def get_directions(user_question: str) -> str:
    """
    Get navigation directions based on a user's question about the campus map.
    Uses both the visual map image and extracted PDF text for comprehensive context.

    Args:
        user_question: The student's question about directions (e.g., "How do I get from the library to the science building?")

    Returns:
        str: Clear, step-by-step directions based on the campus map analysis
    """
    try:
        # Load the encoded map image
        encoded_image = load_map_image()

        # Extract text context from PDF
        pdf_context = extract_pdf_text()

        # Create the message to send to the LLM
        messages = [
            {
                "role": "system",
                "content": (
                    "You are myTigerTrail, an intelligent campus navigation assistant for the University of the Pacific Stockton campus. "
                    "You help students navigate the campus by analyzing the provided map image and any available text context.\n\n"
                    "Your responsibilities:\n"
                    "1. Carefully examine the campus map image to identify buildings, pathways, and landmarks\n"
                    "2. Use any provided PDF text context to enhance your understanding of campus locations and features\n"
                    "3. Listen to the student's direction request (from location X to location Y)\n"
                    "4. Provide clear, step-by-step directions based on what you see in the map and know from the context\n"
                    "5. Include landmark references and estimated walking distances when helpful\n"
                    "6. Be friendly and encouraging in your tone\n\n"
                    "Always base your directions on the visual map image, supplemented by any text context provided. "
                    "Respond with clear, step-by-step directions in English."
                )
            },
            {
                "role": "user",
                "content": f"Here is the UOP Stockton campus map:\n\n[Image attached]\n\nAdditional context from campus documents:\n{pdf_context}\n\nStudent question: {user_question}",
                "images": [encoded_image]
            }
        ]

        response = chat(
            model="gemma3:latest",
            messages=messages,
            stream=False
        )

        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            directions = response.message.content
        else:
            directions = str(response)

        if directions and len(directions.strip()) > 10:  # Basic check for substantial content
            return directions.strip()
        else:
            return "I apologize, but I encountered an issue processing the map. Please try rephrasing your question or check that the campus map files are properly loaded."

    except Exception as e:
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("🐯 Welcome to myTigerTrail - UOP Campus Navigation Assistant 🐯")
    print("=" * 70 + "\n")
    
    try:
        # If a question is provided as command line argument, use it
        if len(sys.argv) > 1:
            question = " ".join(sys.argv[1:])
        else:
            # Otherwise, prompt the user for input
            print("Ask me for directions around the UOP Stockton campus!")
            print("Example: 'How do I get from the library to the science building?'\n")
            question = input("Your question: ").strip()
            
            if not question:
                print("Error: Please provide a direction question.")
                sys.exit(1)
        
        print(f"\n📍 Question: {question}")
        print("\n🔍 Analyzing campus map and generating directions...\n")
        print("-" * 70)
        
        # Get directions from the AI model
        directions = get_directions(question)
        
        print("\n📍 Directions:\n")
        print(directions)
        print("\n" + "-" * 70)
        print("\n✓ Have a great day navigating campus! 🐯\n")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure 'pacific_map.png' exists in the src/ directory")
        print("And optionally 'Pacific-Stk-CampusMap.pdf' for additional context")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Pull the gemma3 model: ollama pull gemma3:latest")
        print("3. Check that the image file is a valid PNG")
        print("4. Try running: python test_llm.py")
        sys.exit(1)

    