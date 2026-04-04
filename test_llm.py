"""
Simple test script to check if Ollama and the LLM are working properly
without image processing.
"""

from ollama import chat

def test_basic_llm():
    """Test basic LLM functionality without images."""
    print("🧪 Testing basic LLM functionality...")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful campus navigation assistant. Respond clearly and concisely."
        },
        {
            "role": "user",
            "content": "How do I get from the library to the science building on a university campus?"
        }
    ]

    try:
        response = chat(
            model="gemma3:latest",
            messages=messages,
            stream=False
        )

        print(f"✓ LLM Response type: {type(response)}")
        print(f"✓ Response attributes: {dir(response)}")

        # Try to access the message content
        if hasattr(response, 'message'):
            content = response.message.content
            print(f"✓ Content length: {len(content)}")
            print(f"✓ Content preview: {content[:200]}...")
            print(f"✓ Full content:\n{content}")
        else:
            print(f"❌ No message attribute found. Response: {response}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_basic_llm()