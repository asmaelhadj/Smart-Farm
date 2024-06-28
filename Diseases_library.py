from app import app, db, Disease  # Make sure to import the necessary objects from your app

def add_diseases():
    diseases = [
        # Apple diseases
        Disease(
            name="Healthy apple",
            plant_type="Apple",
            symptoms="No visible signs of disease. Leaves are green and lush, fruit is developing normally.",
            causes="Optimal growth conditions, adequate nutrition, and absence of pests and diseases.",
            treatments="Continue providing optimal care including proper watering, fertilizing, and monitoring for any signs of stress or disease."
        ),
        Disease(
            name="Diseased: Scab",
            plant_type="Apple",
            symptoms="Dark, scabby lesions on leaves and fruit. Leaves may become twisted and fall prematurely.",
            causes="Caused by the fungus Venturia inaequalis. The disease thrives in wet and humid conditions.",
            treatments="Apply fungicides during the growing season. Remove and destroy infected leaves and fruit to reduce the spread of the disease."
        ),
        Disease(
            name="Diseased: Black rot",
            plant_type="Apple",
            symptoms="Black, sunken lesions on fruit and leaves. Leaves may develop a yellow halo around the lesions.",
            causes="Caused by the fungus Botryosphaeria obtusa. Often enters through wounds or damaged areas on the plant.",
            treatments="Prune out and destroy infected branches. Apply appropriate fungicides and practice good sanitation in the orchard."
        ),
        Disease(
            name="Diseased: Cedar apple rust",
            plant_type="Apple",
            symptoms="Bright orange or yellow spots on leaves. Severe infections can cause premature leaf drop and poor fruit quality.",
            causes="Caused by the fungus Gymnosporangium juniperi-virginianae. Requires both apple and cedar trees to complete its life cycle.",
            treatments="Remove nearby cedar trees if possible. Apply fungicides to apple trees during the spring and early summer."
        ),
        
        # Corn diseases
        Disease(
            name="Healthy corn",
            plant_type="Corn",
            symptoms="No visible signs of disease. Leaves are green and vigorous, with ears developing normally.",
            causes="Optimal growth conditions, adequate nutrition, and absence of pests and diseases.",
            treatments="Continue providing optimal care including proper watering, fertilizing, and monitoring for any signs of stress or disease."
        ),
        Disease(
            name="Diseased: Cercospora leaf spot",
            plant_type="Corn",
            symptoms="Small, tan to brown spots with reddish-brown borders on leaves. Severe infections can cause significant yield loss.",
            causes="Caused by the fungus Cercospora zeae-maydis. The disease thrives in warm, humid conditions.",
            treatments="Apply fungicides at the first sign of disease. Rotate crops and use resistant hybrids if available."
        ),
        Disease(
            name="Diseased: Common rust",
            plant_type="Corn",
            symptoms="Reddish-brown pustules on both upper and lower leaf surfaces. Severe infections can reduce photosynthesis and yield.",
            causes="Caused by the fungus Puccinia sorghi. The disease spreads through windborne spores.",
            treatments="Apply fungicides if the disease appears early in the season. Use resistant hybrids and practice crop rotation."
        ),
        Disease(
            name="Diseased: Northern Leaf Blight",
            plant_type="Corn",
            symptoms="Large, cigar-shaped lesions on leaves. Severe infections can cause significant yield loss and premature plant death.",
            causes="Caused by the fungus Exserohilum turcicum. The disease thrives in cool, humid conditions.",
            treatments="Apply fungicides at the first sign of disease. Use resistant hybrids and practice crop rotation."
        ),
        
        # Grape diseases
        Disease(
            name="Healthy grape",
            plant_type="Grapes",
            symptoms="No visible signs of disease. Leaves are green and vigorous, with clusters developing normally.",
            causes="Optimal growth conditions, adequate nutrition, and absence of pests and diseases.",
            treatments="Continue providing optimal care including proper watering, fertilizing, and monitoring for any signs of stress or disease."
        ),
        Disease(
            name="Diseased: Black rot",
            plant_type="Grapes",
            symptoms="Small, black spots on leaves, stems, and fruit. Infected berries shrivel and become mummified.",
            causes="Caused by the fungus Guignardia bidwellii. The disease thrives in warm, humid conditions.",
            treatments="Apply fungicides during the growing season. Remove and destroy infected plant material to reduce the spread of the disease."
        ),
        Disease(
            name="Diseased: Esca (Black Measles)",
            plant_type="Grapes",
            symptoms="Dark, striped lesions on leaves and berries. Severe infections can cause vine decline and reduced yield.",
            causes="Caused by a complex of fungi including Phaeoacremonium spp. and Phaeomoniella chlamydospora.",
            treatments="Remove and destroy infected plant material. Apply fungicides and practice good sanitation in the vineyard."
        ),
        Disease(
            name="Diseased: Leaf blight (Isariopsis)",
            plant_type="Grapes",
            symptoms="Irregular, brown lesions on leaves. Severe infections can cause defoliation and reduced yield.",
            causes="Caused by the fungus Isariopsis clavispora. The disease thrives in warm, humid conditions.",
            treatments="Apply fungicides during the growing season. Remove and destroy infected plant material to reduce the spread of the disease."
        ),
        
        # Potato diseases
        Disease(
            name="Healthy potato",
            plant_type="Potato",
            symptoms="No visible signs of disease. Leaves are green and vigorous, with tubers developing normally.",
            causes="Optimal growth conditions, adequate nutrition, and absence of pests and diseases.",
            treatments="Continue providing optimal care including proper watering, fertilizing, and monitoring for any signs of stress or disease."
        ),
        Disease(
            name="Diseased: Early blight",
            plant_type="Potato",
            symptoms="Small, dark lesions on leaves with concentric rings. Severe infections can cause defoliation and reduced yield.",
            causes="Caused by the fungus Alternaria solani. The disease thrives in warm, humid conditions.",
            treatments="Apply fungicides at the first sign of disease. Rotate crops and use resistant varieties if available."
        ),
        Disease(
            name="Diseased: Late blight",
            plant_type="Potato",
            symptoms="Large, water-soaked lesions on leaves and stems. Infected tubers may rot in storage.",
            causes="Caused by the oomycete Phytophthora infestans. The disease thrives in cool, wet conditions.",
            treatments="Apply fungicides at the first sign of disease. Rotate crops and use resistant varieties if available."
        ),
        
        # Tomato diseases
        Disease(
            name="Healthy tomato",
            plant_type="Tomato",
            symptoms="No visible signs of disease. Leaves are green and vigorous, with fruit developing normally.",
            causes="Optimal growth conditions, adequate nutrition, and absence of pests and diseases.",
            treatments="Continue providing optimal care including proper watering, fertilizing, and monitoring for any signs of stress or disease."
        ),
        Disease(
            name="Diseased: Bacterial spot",
            plant_type="Tomato",
            symptoms="Small, water-soaked spots on leaves, stems, and fruit. Spots may coalesce, causing significant defoliation.",
            causes="Caused by the bacterium Xanthomonas campestris pv. vesicatoria. The disease thrives in warm, wet conditions.",
            treatments="Apply copper-based bactericides. Rotate crops and avoid overhead watering to reduce the spread of the disease."
        ),
        Disease(
            name="Diseased: Early blight",
            plant_type="Tomato",
            symptoms="Small, dark lesions on leaves with concentric rings. Severe infections can cause defoliation and reduced yield.",
            causes="Caused by the fungus Alternaria solani. The disease thrives in warm, humid conditions.",
            treatments="Apply fungicides at the first sign of disease. Rotate crops and use resistant varieties if available."
        ),
        Disease(
            name="Diseased: Late blight",
            plant_type="Tomato",
            symptoms="Large, water-soaked lesions on leaves and stems. Infected fruit may rot on the vine.",
            causes="Caused by the oomycete Phytophthora infestans. The disease thrives in cool, wet conditions.",
            treatments="Apply fungicides at the first sign of disease. Rotate crops and use resistant varieties if available."
        ),
        Disease(
            name="Diseased: Septoria leaf spot",
            plant_type="Tomato",
            symptoms="Small, circular lesions on leaves with dark borders. Severe infections can cause significant defoliation.",
            causes="Caused by the fungus Septoria lycopersici. The disease thrives in warm, wet conditions.",
            treatments="Apply fungicides at the first sign of disease. Rotate crops and use resistant varieties if available."
        ),
        Disease(
            name="Diseased: Yellow Leaf Curl Virus",
            plant_type="Tomato",
            symptoms="Yellowing and curling of leaves, stunted growth, and reduced yield.",
            causes="Caused by the Tomato yellow leaf curl virus (TYLCV), transmitted by whiteflies.",
            treatments="Control whitefly populations using insecticides and reflective mulches. Use resistant varieties if available."
        ),
    ]

    for disease in diseases:
        db.session.add(disease)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This creates the tables based on the models if they don't exist
        add_diseases()
