import os
from PIL import Image

# Configuration
INPUT_IMAGE_PATH = r"C:\Users\bayin\.gemini\antigravity\brain\01294673-1376-4969-b4bf-62d657b632c0\media__1770408484705.png"
APP_DIR = os.getcwd()
ASSETS_DIR = os.path.join(APP_DIR, "assets")
OUTPUT_PATH = os.path.join(ASSETS_DIR, "logo_final.png") # V4/Final

# Theme Color
THEME_BG = (30, 41, 59, 255) # #1e293b

def is_cyan_ish(r, g, b):
    # Keep pixel if it has significant Green/Blue component compared to Red
    # Cyan is roughly (0, 255, 255).
    # We want to keep anything "colorful" that isn't white/grey background
    # But wait, "Beyin Sporu" is grey.
    return (g > r + 30) or (b > r + 30)

def is_text_grey_ish(r, g, b):
    # Beyin Sporu is dark grey
    # Background is likely lighter.
    # Keep dark pixels.
    return r < 180 and g < 180 and b < 180

def process_logo():
    print(f"Starting final logo fix...")
    
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    try:
        img = Image.open(INPUT_IMAGE_PATH)
        print(f"Original Size: {img.size}")
        
        # Resize first to 1800
        target_width = 1800
        if img.size[0] != target_width:
             ratio = target_width / float(img.size[0])
             target_height = int(float(img.size[1]) * ratio)
             img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
             print(f"Resized to: {img.size}")

        img_rgba = img.convert("RGBA")
        datas = img_rgba.getdata()
        
        new_data = []
        changed_pixels = 0
        total_pixels = len(datas)

        for item in datas:
            r, g, b, a = item
            
            # LOGIC:
            # If it looks like the background (Light/White), replace it.
            # If it looks like the text (Cyan or Dark Grey), keep it.
            
            # Simple brightness check:
            # If pixel is very bright (likely white background), replace it
            brightness = (r + g + b) // 3
            
            if brightness > 220: # White/Light Grey Background
                new_data.append(THEME_BG)
                changed_pixels += 1
            elif brightness > 150 and abs(r-g) < 20 and abs(r-b) < 20: # Lighter greys (noise?)
                 new_data.append(THEME_BG)
                 changed_pixels += 1
            else:
                # Keep pixel (Text)
                # Ensure it's opaque if we want solid look, or keep original alpha
                new_data.append(item)

        print(f"Processed. Changed {changed_pixels} of {total_pixels} pixels ({(changed_pixels/total_pixels)*100:.1f}%)")
        
        img_rgba.putdata(new_data)
        img_rgba.save(OUTPUT_PATH)
        print(f"Saved final logo to: {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_logo()
