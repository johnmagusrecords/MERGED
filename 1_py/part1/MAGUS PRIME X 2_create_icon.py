from PIL import Image

# Save a basic icon as a placeholder
img = Image.new("RGBA", (256, 256), color=(0, 50, 100, 255))
img.save(
    "MAGUS_PRIME_X_icon.ico",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("Icon file created successfully.")
