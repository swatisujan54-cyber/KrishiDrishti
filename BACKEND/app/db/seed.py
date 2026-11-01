"""Seed data for the KrishiDrishti database.

Creates a database-backed list of supported crops, demonstration disease
records with advisory information, and sample translations.

IMPORTANT: Disease advisory content here is **demonstration data** marked with
``review_status = demonstration``.  Before production use, all advisory text
must be reviewed and confirmed by a qualified agricultural expert.

Run with::

    python -m app.db.seed
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.crop import Crop
from app.models.disease import Disease, DiseaseTranslation, ReviewStatus

logger = logging.getLogger("krishidrishti.seed")

# --------------------------------------------------------------------------- #
# Crop seed data                                                               #
# --------------------------------------------------------------------------- #

CROPS = [
    {
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "description": "Widely cultivated vegetable crop; sensitive to fungal and bacterial diseases.",
        "is_supported": True,
    },
    {
        "name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "description": "Major tuber crop; vulnerable to blight and leaf diseases.",
        "is_supported": True,
    },
    {
        "name": "Rice",
        "scientific_name": "Oryza sativa",
        "description": "Staple cereal crop in India; susceptible to blast and brown spot.",
        "is_supported": True,
    },
    {
        "name": "Maize",
        "scientific_name": "Zea mays",
        "description": "Important cereal crop; affected by rust and leaf blight.",
        "is_supported": True,
    },
    {
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "description": "Major staple cereal; rust and smut diseases are common.",
        "is_supported": True,
    },
    {
        "name": "Chilli",
        "scientific_name": "Capsicum annuum",
        "description": "Common spice crop; affected by leaf spot and viral diseases.",
        "is_supported": False,
    },
]

# --------------------------------------------------------------------------- #
# Disease seed data (DEMONSTRATION ONLY)                                      #
# --------------------------------------------------------------------------- #
# Each entry maps a crop name (must match CROPS above) to disease details.
# ``label_key`` connects to the model output label in ml/labels.json.

DISEASES = [
    # --- Tomato ---
    {
        "crop": "Tomato",
        "name": "Early Blight",
        "label_key": "Tomato___Early_blight",
        "symptoms": (
            "Dark brown to black spots with concentric rings (target-like) on "
            "older leaves.  Affected leaves may yellow and drop.  Lesions can "
            "also appear on stems and fruits."
        ),
        "possible_causes": (
            "Caused by the fungus Alternaria solani.  Favoured by warm, humid "
            "weather and prolonged leaf wetness."
        ),
        "preventive_measures": (
            "Use disease-free seed, practice crop rotation, remove infected "
            "plant debris, improve air circulation, and avoid overhead "
            "irrigation."
        ),
        "recommended_next_steps": (
            "Remove and destroy affected leaves.  Apply a recommended "
            "fungicide following label directions.  Consult a local "
            "agricultural officer if symptoms spread rapidly."
        ),
        "expert_consultation_guidance": (
            "If symptoms are severe or you are unsure of the diagnosis, submit "
            "a sample or image for expert review through the platform."
        ),
        "advisory_source": "KrishiDrishti demonstration data — unreviewed",
    },
    {
        "crop": "Tomato",
        "name": "Late Blight",
        "label_key": "Tomato___Late_blight",
        "symptoms": (
            "Large, irregular, water-soaked lesions on leaves that turn brown. "
            "White fungal growth may appear on the underside of leaves in humid "
            "conditions.  Fruits develop firm, dark brown patches."
        ),
        "possible_causes": (
            "Caused by the oomycete Phytophthora infestans.  Spreads rapidly in "
            "cool, wet weather."
        ),
        "preventive_measures": (
            "Use resistant varieties, avoid planting in low-lying areas, "
            "ensure good drainage, and remove infected plants promptly."
        ),
        "recommended_next_steps": (
            "Remove infected plants immediately.  Apply appropriate fungicide "
            "as per label and local regulations.  Seek expert advice for "
            "large-scale outbreaks."
        ),
        "expert_consultation_guidance": (
            "Late blight spreads fast — request expert consultation early to "
            "protect the crop."
        ),
        "advisory_source": "KrishiDrishti demonstration data — unreviewed",
    },
    # --- Potato ---
    {
        "crop": "Potato",
        "name": "Early Blight",
        "label_key": "Potato___Early_blight",
        "symptoms": (
            "Dark, circular lesions with concentric rings on lower leaves. "
            "Leaves may yellow and die prematurely, reducing tuber yield."
        ),
        "possible_causes": (
            "Caused by Alternaria solani.  Warm temperatures and extended leaf "
            "wetness promote infection."
        ),
        "preventive_measures": (
            "Rotate crops, use certified disease-free seed tubers, maintain "
            "adequate plant spacing, and remove crop debris after harvest."
        ),
        "recommended_next_steps": (
            "Remove infected foliage.  Apply a labelled fungicide.  Consult a "
            "local agricultural extension officer for guidance."
        ),
        "expert_consultation_guidance": (
            "Submit an image for expert review if the diagnosis is uncertain."
        ),
        "advisory_source": "KrishiDrishti demonstration data — unreviewed",
    },
    # --- Rice ---
    {
        "crop": "Rice",
        "name": "Brown Spot",
        "label_key": "Rice___brown_spot",
        "symptoms": (
            "Small, oval, brown spots with a grey or tan centre on leaves. "
            "Severe infection can cause grain discoloration and reduced yield."
        ),
        "possible_causes": (
            "Caused by the fungus Bipolaris oryzae.  More common in nutrient-"
            "deficient soils and under water stress."
        ),
        "preventive_measures": (
            "Use healthy seed, maintain balanced soil nutrition, ensure "
            "proper water management, and treat seed with fungicide before "
            "sowing."
        ),
        "recommended_next_steps": (
            "Improve soil fertility.  Apply a recommended fungicide following "
            "label instructions.  Consult an expert for persistent outbreaks."
        ),
        "expert_consultation_guidance": (
            "If symptoms persist after treatment, request expert review to "
            "confirm the diagnosis."
        ),
        "advisory_source": "KrishiDrishti demonstration data — unreviewed",
    },
    # --- Maize ---
    {
        "crop": "Maize",
        "name": "Common Rust",
        "label_key": "Maize___common_rust",
        "symptoms": (
            "Small, reddish-brown raised pustules on both leaf surfaces. "
            "Heavily infected leaves may turn yellow and dry out."
        ),
        "possible_causes": (
            "Caused by the fungus Puccinia sorghi.  Favoured by moderate "
            "temperatures and high humidity."
        ),
        "preventive_measures": (
            "Plant resistant hybrids, avoid late planting, and remove "
            "volunteer plants."
        ),
        "recommended_next_steps": (
            "Monitor the crop regularly.  If infection is widespread, consult "
            "a local agricultural officer about fungicide options."
        ),
        "expert_consultation_guidance": (
            "Send an image for expert review if you are unsure whether it is "
            "common rust or another disease."
        ),
        "advisory_source": "KrishiDrishti demonstration data — unreviewed",
    },
]

# Sample Hindi translations for a subset of diseases.
TRANSLATIONS = [
    {
        "disease": "Early Blight",
        "crop": "Tomato",
        "language": "hi",
        "name": "प्रारंभिक झुलसा",
        "symptoms": (
            "पुरानी पत्तियों पर गहरे भूरे से काले धब्बे एकाग्र छल्लों के साथ "
            "दिखाई देते हैं। प्रभावित पत्तियाँ पीली होकर गिर सकती हैं।"
        ),
        "possible_causes": (
            "यह एक कवक (Alternaria solani) के कारण होता है, जो गर्म और नम "
            "मौसम में फैलता है।"
        ),
        "preventive_measures": (
            "रोगमुक्त बीज का उपयोग करें, फसल चक्र अपनाएँ, संक्रमित अवशेष "
            "हटाएँ, और हवा का प्रवाह बेहतर बनाएँ।"
        ),
        "recommended_next_steps": (
            "प्रभावित पत्तियाँ हटाएँ। अनुमोदित फफूंदनाशक का उपयोग करें और "
            "स्थानीय कृषि अधिकारी से परामर्श लें।"
        ),
        "expert_consultation_guidance": (
            "यदि निदान अनिश्चित है, तो विशेषज्ञ समीक्षा के लिए छवि भेजें।"
        ),
        "advisory_source": "KrishiDrishti प्रदर्शन डेटा — असमीक्षित",
    },
]


def _get_or_create_crop(db: Session, data: dict) -> Crop:
    """Return an existing Crop by name or create a new one."""
    crop = db.execute(select(Crop).where(Crop.name == data["name"])).scalar_one_or_none()
    if crop is None:
        crop = Crop(**data)
        db.add(crop)
        db.flush()
        logger.info("Created crop: %s", data["name"])
    return crop


def _get_or_create_disease(db: Session, crop: Crop, data: dict) -> Disease:
    """Return an existing Disease by (crop_id, name) or create a new one."""
    disease = db.execute(
        select(Disease).where(Disease.crop_id == crop.id, Disease.name == data["name"])
    ).scalar_one_or_none()
    if disease is None:
        disease = Disease(
            crop_id=crop.id,
            name=data["name"],
            label_key=data.get("label_key"),
            symptoms=data.get("symptoms"),
            possible_causes=data.get("possible_causes"),
            preventive_measures=data.get("preventive_measures"),
            recommended_next_steps=data.get("recommended_next_steps"),
            expert_consultation_guidance=data.get("expert_consultation_guidance"),
            advisory_source=data.get("advisory_source"),
            review_status=ReviewStatus.demonstration,
        )
        db.add(disease)
        db.flush()
        logger.info("Created disease: %s -> %s", crop.name, data["name"])
    return disease


def _get_or_create_translation(db: Session, disease: Disease, data: dict) -> None:
    """Create a translation if it doesn't already exist."""
    existing = db.execute(
        select(DiseaseTranslation).where(
            DiseaseTranslation.disease_id == disease.id,
            DiseaseTranslation.language == data["language"],
        )
    ).scalar_one_or_none()
    if existing is None:
        tr = DiseaseTranslation(
            disease_id=disease.id,
            language=data["language"],
            name=data.get("name"),
            symptoms=data.get("symptoms"),
            possible_causes=data.get("possible_causes"),
            preventive_measures=data.get("preventive_measures"),
            recommended_next_steps=data.get("recommended_next_steps"),
            expert_consultation_guidance=data.get("expert_consultation_guidance"),
            advisory_source=data.get("advisory_source"),
            review_status=ReviewStatus.demonstration,
        )
        db.add(tr)
        db.flush()
        logger.info("Created translation: %s [%s]", disease.name, data["language"])


def run_seed(db: Session | None = None) -> None:
    """Insert all seed data.  Safe to run multiple times (idempotent)."""
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        # Crops
        crop_map: dict[str, Crop] = {}
        for crop_data in CROPS:
            crop = _get_or_create_crop(db, crop_data)
            crop_map[crop.name] = crop

        # Diseases
        for disease_data in DISEASES:
            crop = crop_map.get(disease_data["crop"])
            if crop is None:
                logger.warning("Crop not found for disease: %s", disease_data["crop"])
                continue
            _get_or_create_disease(db, crop, disease_data)

        # Translations
        for tr_data in TRANSLATIONS:
            crop = crop_map.get(tr_data["crop"])
            if crop is None:
                continue
            disease = db.execute(
                select(Disease).where(
                    Disease.crop_id == crop.id, Disease.name == tr_data["disease"]
                )
            ).scalar_one_or_none()
            if disease is None:
                continue
            _get_or_create_translation(db, disease, tr_data)

        db.commit()
        logger.info("Seed data inserted successfully.")
    except Exception:
        db.rollback()
        logger.exception("Seed failed — rolling back.")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_seed()
