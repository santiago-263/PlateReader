# Plate reader

import cv2
import numpy as np
import pandas as pd
# If not installed, run:
# pip install pandas
# pip install numpy
# pip install opencv-python

# For Visual Studio users:
# If cv2 is not recognized, go to settings (...) (Top right corner)
# Configure Editors -> Open Settings (JSON)
# Add the following:
# "workbench.colorTheme": "Quiet Light",
#    "pylint.args": ["cv2"]
# ...
# This resolves the cv2 import error


# Load the image that contains the ELISA plate
# Make sure the image is cropped to show only the wells area
imagen_path = 'Transiluminador-ASR.png'  # Change according to your image file name and extension
imagen = cv2.imread(imagen_path)

# Get image dimensions to define the ELISA plate area
alto_imagen, ancho_imagen = imagen.shape[:2]

# The ELISA plate has n rows and m columns
filas = 8
columnas = 12

# You can adjust the offset to the left/right or up/down
desplazamiento_x = -5  # (+) Left, (-) Right
desplazamiento_y = -33  # (+) Up, (-) Down

# Determine well size based on image dimensions
factor_reduccion = 0.2  # Adjust area read from the wells with a scaling factor
radio_pozo = int(min(ancho_imagen // (2 * (columnas + 1)), alto_imagen // (2 * (filas + 1))) * factor_reduccion)
espacio_horizontal = ancho_imagen // (columnas + 1)
espacio_vertical = alto_imagen // (filas + 1)

# Convert image to grayscale
imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

# Important: the image should reflect natural lighting, otherwise the program may misinterpret the data
imagen_invertida = 255 - imagen_gris  # Invert grayscale image to emphasize intensity

# List to store intensities
intensidades = []

# Read each well in typical ELISA reader order
for i in range(filas):
    fila_intensidades = []
    for j in range(columnas):
        # Determine center coordinates of each well
        centro_x = (j + 1) * espacio_horizontal - desplazamiento_x
        centro_y = (i + 1) * espacio_vertical - desplazamiento_y

        # Draw a circle to represent the well
        cv2.circle(imagen, (centro_x, centro_y), radio_pozo, (0, 0, 0), 2)

        # Create a mask to quantify well intensity
        mascara = np.zeros_like(imagen_invertida)
        cv2.circle(mascara, (centro_x, centro_y), radio_pozo, 255, -1)

        # Compute average intensity within the well using the inverted image
        intensidad_media = cv2.mean(imagen_invertida, mask=mascara)[0]

        # Simulate absorbance: A = -log10(T), where T is transmittance (normalized intensity)
        transmitancia = intensidad_media / 255.0
        # Avoid log(0) error by setting a minimum value
        if transmitancia <= 0:
            transmitancia = 0.001  # Minimum value

        # Calculate simulated absorbance
        absorbancia = -np.log10(transmitancia)
        fila_intensidades.append(absorbancia)

    intensidades.append(fila_intensidades)

# Save inverted image
cv2.imwrite('Placa_ELISA_Invertida.png', imagen)

# Optionally display the inverted image (for visual verification, not saved)
# cv2.namedWindow('Inverted Image', cv2.WINDOW_NORMAL)
# cv2.imshow('Inverted Image', imagen_invertida)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Display the annotated image with circles (saved version)
cv2.namedWindow('ELISA Plate', cv2.WINDOW_NORMAL)
cv2.imshow('ELISA Plate', imagen)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save intensities to a CSV file
datos_pozo = pd.DataFrame(intensidades, 
                          columns=[f'Column {j+1}' for j in range(columnas)],
                          index=[f'Row {i+1}' for i in range(filas)])

datos_pozo.to_csv('Intensities.csv')
print("File 'Intensities.csv' successfully generated.")

# To process the image in Excel:
# Go to Excel -> Data -> Get Data -> From File -> CSV -> Import
