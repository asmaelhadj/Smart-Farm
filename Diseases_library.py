from app import app, db, Disease  # Make sure to import the necessary objects from your app

def add_diseases():
    disease1 = Disease(
        name="Powdery Mildew",
        plant_type="Rose",
        symptoms="White powdery spots on leaves and stems.",
        causes="Fungal infection.",
        treatments="Fungicides, remove infected parts."
    )
    disease2 = Disease(
        name="Downy Mildew",
        plant_type="Grape",
        symptoms="Yellow spots on leaves, white mold on underside.",
        causes="Fungal infection.",
        treatments="Fungicides, improve air circulation."
    )
    db.session.add(disease1)
    db.session.add(disease2)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This creates the tables based on the models if they don't exist
        add_diseases()
