import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import sqlite3
import numpy as np
import face_recognition
import os

# -------------------- Database --------------------
DB_FILE = "faces.db"

def load_database():
    """Load all face embeddings from SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filename, embedding FROM faces")
    rows = c.fetchall()
    conn.close()

    database = {}
    for filename, embedding_blob in rows:
        database[filename] = np.frombuffer(embedding_blob, dtype=np.float64)
    return database

def find_most_similar(query_image, database):
    try:
        image = face_recognition.load_image_file(query_image)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) == 0:
            return None, None
        query_embedding = encodings[0]

        min_dist = float("inf")
        most_similar = None

        for filename, db_embedding in database.items():
            dist = np.linalg.norm(query_embedding - db_embedding)
            if dist < min_dist:
                min_dist = dist
                most_similar = filename

        return most_similar, min_dist
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# -------------------- GUI --------------------
class FaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Similarity Finder")
        self.root.geometry("900x700")
        self.root.configure(bg="#2c3e50")  # Dark background

        # Load database once
        self.database = load_database()

        self.query_image_path = None

        # Title Label
        self.title_label = tk.Label(root, text="Face Similarity Finder", 
                                    font=("Helvetica", 24, "bold"),
                                    fg="white", bg="#2c3e50")
        self.title_label.pack(pady=20)

        # Frames for images
        self.frame_images = tk.Frame(root, bg="#34495e", bd=0)
        self.frame_images.pack(pady=20, padx=20, fill="x")

        # Uploaded image
        self.upload_frame = tk.Frame(self.frame_images, bg="#34495e", bd=0)
        self.upload_frame.pack(side="left", padx=40)
        tk.Label(self.upload_frame, text="Uploaded Image", 
                 bg="#34495e", fg="white", font=("Helvetica", 14)).pack()
        self.img_canvas = tk.Label(self.upload_frame, bg="#34495e")
        self.img_canvas.pack(pady=10)

        # Similar image
        self.similar_frame = tk.Frame(self.frame_images, bg="#34495e", bd=0)
        self.similar_frame.pack(side="right", padx=40)
        tk.Label(self.similar_frame, text="Most Similar Image", 
                 bg="#34495e", fg="white", font=("Helvetica", 14)).pack()
        self.similar_canvas = tk.Label(self.similar_frame, bg="#34495e")
        self.similar_canvas.pack(pady=10)

        # Buttons
        self.button_frame = tk.Frame(root, bg="#2c3e50")
        self.button_frame.pack(pady=20)

        self.browse_btn = tk.Button(self.button_frame, text="Browse Image", 
                                    font=("Helvetica", 12, "bold"),
                                    bg="#1abc9c", fg="white", activebackground="#16a085",
                                    relief="flat", padx=20, pady=10, command=self.browse_image)
        self.browse_btn.pack(side="left", padx=20)

        self.find_btn = tk.Button(self.button_frame, text="Find Most Similar", 
                                  font=("Helvetica", 12, "bold"),
                                  bg="#e74c3c", fg="white", activebackground="#c0392b",
                                  relief="flat", padx=20, pady=10, command=self.find_similar)
        self.find_btn.pack(side="right", padx=20)

        # Similarity score
        self.score_label = tk.Label(root, text="", font=("Helvetica", 16, "bold"), 
                                    fg="white", bg="#2c3e50")
        self.score_label.pack(pady=20)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.query_image_path = file_path
            self.show_image(file_path, self.img_canvas)

    def show_image(self, path, canvas):
        try:
            img = Image.open(path)
            img = img.resize((250, 250))
            img = ImageOps.expand(img, border=2, fill="#ecf0f1")  # border to simulate card
            img_tk = ImageTk.PhotoImage(img)
            canvas.image = img_tk
            canvas.config(image=img_tk)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")

    def find_similar(self):
        if not self.query_image_path:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return

        most_similar, score = find_most_similar(self.query_image_path, self.database)
        if most_similar:
            self.show_image(most_similar, self.similar_canvas)
            self.score_label.config(text=f"Similarity Score (Euclidean distance): {score:.4f}")
        else:
            messagebox.showinfo("Info", "No similar face found!")

# -------------------- Main --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceApp(root)
    root.mainloop()
