import cv2
import face_recognition


# Main loop
def detect(img_path, reference_img):

    # Load the reference image
    reference_image = face_recognition.load_image_file(reference_img)
    reference_encoding = face_recognition.face_encodings(reference_image)[0]

    # Load the uploaded image file
    img = face_recognition.load_image_file(img_path)

    # Find all the faces and their encodings in the current frame
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    # Iterate over detected faces
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the face encoding with the reference encoding
        matches = face_recognition.compare_faces([reference_encoding], face_encoding)
        if matches[0]:
            print("Face recognized, login successful!")
            return True
        else:
            print("Invalid login!")
            return False


