from PIL import Image
import pytesseract

image = Image.open("sample_image.png")
text = pytesseract.image_to_string(image)
print(text.strip())