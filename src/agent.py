from ollama import chat

#myTigerTrail~~~~~

#The codebase will use a picture to extract data from map.  
def get_directions(): 
    image_path = "path/<MAP_IMAGE_HERE>.jpg"  
    messages = [
        {
            "role": "system", #Specify role as system.
            "content": (
                "You are an assistant for UOP's map navigation app, "myTigerTrail"! You will help users navigate the campus map.\n\n"
                "Your task is to:\n"
            )
        },
        {
            "role": "user",  #Specify role as user.
            "content": uploaded_file_text
        }
    ]
    response = chat(model="gemma3:latest", messages=messages)
    
    return pantry_dict

if __name__ == "__main__":
    