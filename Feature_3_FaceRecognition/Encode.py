import face_recognition as fr
import pickle
import os
import numpy as np

def encode_faces(directory_path, output_file):
    """Encodes faces from images in a directory and saves the encodings to a file.

    Args:
        directory_path (str): Path to the directory containing face images.
        output_file (str): Path to the output file for saving the encodings.
    """

    encoded_faces = {}

    for person_folder in os.listdir(directory_path):
        person_folder_path = os.path.join(directory_path, person_folder)

        if os.path.isdir(person_folder_path):
            person_name = person_folder  # Assuming subfolder name is person's name
            person_encodings = []

            for image_filename in os.listdir(person_folder_path):
                if image_filename.endswith((".jpg", ".png")):
                    image_path = os.path.join(person_folder_path, image_filename)

                    try:
                        image = fr.load_image_file(image_path)
                        face_encodings = fr.face_encodings(image)

                        if face_encodings:
                            # Use the first face encoding
                            encoding = face_encodings[0]
                            person_encodings.append(encoding)
                        else:
                            print(f"No face found in {image_path}. Skipping.")
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")

            if person_encodings:
                avg_encoding = np.mean(person_encodings, axis=0)
                encoded_faces[person_name] = avg_encoding
                print(f"Encoded {len(person_encodings)} images for '{person_name}'.")

    with open(output_file, "wb") as file:
        pickle.dump(encoded_faces, file)

if __name__ == "__main__":
    input_directory = "./faces"  # Directory containing face images
    output_file_path = "encodingfile"  # Output file for encodings

    encode_faces(input_directory, output_file_path)
