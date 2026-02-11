
import json
import sys

# Configuration
FILE_PATH = 'c:/Application/Kelime_Oyunu/sozluk.json'
KEYS_TO_REMOVE = ['3_harf', '11_harf', '12_harf', '13_harf']

def cleanup_sozluk():

        log_file = open('cleanup_debug.txt', 'w', encoding='utf-8')
        sys.stdout = log_file
        sys.stderr = log_file

        print(f"Reading {FILE_PATH}...")
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        initial_keys = list(data.keys())
        print(f"Initial keys: {initial_keys}")
        
        removed_count = 0
        for key in KEYS_TO_REMOVE:
            if key in data:
                del data[key]
                print(f"Removed key: {key}")
                removed_count += 1
            else:
                print(f"Key not found: {key}")
        
        if removed_count == 0:
            print("No keys removed. But proceeding to save anyway to ensure consistency if keys were already gone.")
        
        print(f"Saving changes to {FILE_PATH}...")
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print("Cleanup complete.")
        
        # Verify
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            verify_data = json.load(f)
        
        remaining_keys = list(verify_data.keys())
        print(f"Remaining keys: {remaining_keys}")
        
        for key in KEYS_TO_REMOVE:
            if key in remaining_keys:
                print(f"ERROR: Key {key} still exists!")
                sys.exit(1)
        
        print("Verification successful.")
        log_file.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        try:
            log_file.close()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    cleanup_sozluk()
