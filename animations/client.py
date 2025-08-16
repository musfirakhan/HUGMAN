import argparse
import requests
import sys  

def generate_animation(prompt: str, output_path: str) -> bool:  # Added return type
    try:
        response = requests.post(
            "http://192.168.1.12:8000/generate_animation",
            json={"prompt": prompt}
        )
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Success: BVH saved to {output_path}")
            return True  # Explicit success
        else:
            print(f"Error: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Failed: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('prompt', type=str)
    parser.add_argument('output_path', type=str)
    args = parser.parse_args()
    
    success = generate_animation(args.prompt, args.output_path)
    sys.exit(0 if success else 1)  