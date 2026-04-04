"""
Example usage script for myTigerTrail Navigation Assistant.

This script demonstrates how to use the get_directions function locally
without needing to run the FastAPI server.
"""

from src.agent import get_directions


def main():
    """Run example direction requests."""
    
    print("=" * 60)
    print("myTigerTrail - Campus Navigation Assistant")
    print("=" * 60)
    print()
    
    # Example questions a student might ask
    example_questions = [
        "How do I get from the main entrance to the science building?",
        "Where is the library and how do I get there from the student center?",
        "Can you help me find my way to the athletic center?",
    ]
    
    # Demonstrate with the first example (you can modify this)
    print("Example: Getting directions on campus\n")
    
    question = "How do I get from the parking lot to the engineering building?"
    print(f"Question: {question}\n")
    
    try:
        print("Fetching directions from myTigerTrail...\n")
        directions = get_directions(question)
        
        print("Directions:")
        print("-" * 60)
        print(directions)
        print("-" * 60)
    
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. Ollama is installed and running")
        print("2. The gemma3 model is downloaded: ollama pull gemma3")
        print("3. The campus map image (uop-stockton-campus-map.jpg) exists in ./src/")


if __name__ == "__main__":
    main()
