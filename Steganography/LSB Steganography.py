#!/usr/bin/env python3
"""
LSB Steganography Tool for CTF Challenge Creation
Usage:
    python stego_tool.py encode input.png "CTF{your_flag}" output.png
    python stego_tool.py decode stego_image.png
"""

from PIL import Image
import sys

def encode_lsb(input_path, message, output_path):
    """Hide a message in an image using LSB steganography"""
    try:
        img = Image.open(input_path)
        img = img.convert('RGB')  # Ensure RGB mode
        pixels = list(img.getdata())
        width, height = img.size
        
        # Add delimiter to mark end of message
        message_with_delimiter = message + "|||END|||"
        
        # Convert message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message_with_delimiter)
        
        # Check if message fits in image
        if len(binary_message) > len(pixels) * 3:
            print(f"❌ Error: Message too long! Maximum {len(pixels) * 3 // 8} characters.")
            return False
        
        # Encode message in LSB of pixels
        new_pixels = []
        binary_index = 0
        
        for pixel in pixels:
            r, g, b = pixel
            
            # Encode in red channel
            if binary_index < len(binary_message):
                r = (r & 0xFE) | int(binary_message[binary_index])
                binary_index += 1
            
            # Encode in green channel
            if binary_index < len(binary_message):
                g = (g & 0xFE) | int(binary_message[binary_index])
                binary_index += 1
            
            # Encode in blue channel
            if binary_index < len(binary_message):
                b = (b & 0xFE) | int(binary_message[binary_index])
                binary_index += 1
            
            new_pixels.append((r, g, b))
        
        # Create new image with hidden message
        stego_img = Image.new('RGB', (width, height))
        stego_img.putdata(new_pixels)
        stego_img.save(output_path, 'PNG')
        
        print(f"✅ Success! Message hidden in {output_path}")
        print(f"📊 Message length: {len(message)} characters")
        print(f"🔒 Hidden bits: {len(binary_message)}")
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_path}' not found!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def decode_lsb(image_path):
    """Extract hidden message from stego image"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = list(img.getdata())
        
        # Extract LSB from each color channel
        binary_message = ''
        for pixel in pixels:
            r, g, b = pixel
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
        
        # Convert binary to text
        message = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i+8]
            if len(byte) == 8:
                char = chr(int(byte, 2))
                message += char
                
                # Check for delimiter
                if message.endswith('|||END|||'):
                    message = message.replace('|||END|||', '')
                    print(f"✅ Hidden message found!")
                    print(f"🚩 Message: {message}")
                    return message
        
        print("❌ No hidden message found (or wrong format)")
        return None
        
    except FileNotFoundError:
        print(f"❌ Error: File '{image_path}' not found!")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def create_sample_image(filename="sample.png", width=400, height=300):
    """Create a sample image for testing"""
    from PIL import ImageDraw, ImageFont
    
    img = Image.new('RGB', (width, height), color=(70, 130, 180))
    draw = ImageDraw.Draw(img)
    
    # Add some visual elements
    for i in range(0, width, 40):
        draw.line([(i, 0), (i, height)], fill=(100, 150, 200), width=2)
    for i in range(0, height, 40):
        draw.line([(0, i), (width, i)], fill=(100, 150, 200), width=2)
    
    # Add text
    try:
        draw.text((width//2 - 80, height//2 - 10), "CTF Challenge", fill=(255, 255, 255))
    except:
        pass
    
    img.save(filename, 'PNG')
    print(f"✅ Sample image created: {filename}")
    return filename


def print_usage():
    """Print usage instructions"""
    print("""
🔍 LSB Steganography Tool for CTF Challenges

USAGE:
    Encode (hide message):
        python stego_tool.py encode <input_image> "<message>" <output_image>
    
    Decode (extract message):
        python stego_tool.py decode <stego_image>
    
    Create sample image:
        python stego_tool.py sample [filename]

EXAMPLES:
    # Hide a flag in an image
    python stego_tool.py encode cat.png "picoCTF{hidden_in_pixels}" challenge.png
    
    # Extract hidden message
    python stego_tool.py decode challenge.png
    
    # Create a sample image for testing
    python stego_tool.py sample test.png

TIPS:
    - Use PNG format for best results (lossless)
    - Avoid JPEG (lossy compression destroys hidden data)
    - Message is invisible to human eye
    - Solvers can use: zsteg, stegsolve, or this script
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "encode":
        if len(sys.argv) != 5:
            print("❌ Error: Wrong number of arguments for encode")
            print("Usage: python stego_tool.py encode <input> <message> <output>")
            return
        
        input_image = sys.argv[2]
        message = sys.argv[3]
        output_image = sys.argv[4]
        
        encode_lsb(input_image, message, output_image)
    
    elif command == "decode":
        if len(sys.argv) != 3:
            print("❌ Error: Wrong number of arguments for decode")
            print("Usage: python stego_tool.py decode <stego_image>")
            return
        
        stego_image = sys.argv[2]
        decode_lsb(stego_image)
    
    elif command == "sample":
        filename = sys.argv[2] if len(sys.argv) > 2 else "sample.png"
        create_sample_image(filename)
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()