from app.models.consultation import Prescription
from app.schemas.consultation import PrescriptionCreate



def treatments_are_identical(
    existing_prescriptions: list[Prescription],
    new_prescriptions: list[PrescriptionCreate],
) -> bool:
    """Compara las prescripciones del tratamiento activo contra las nuevas."""
    if len(existing_prescriptions) != len(new_prescriptions):
        return False

    def to_comparable_existing(p: Prescription) -> tuple[str, str, str, str, str, str]:
        return (
            p.medication_name.strip().lower(),
            p.dose.strip().lower(),
            p.frequency.strip().lower(),
            p.duration.strip().lower(),
            str(p.route),
            (p.instructions or "").strip().lower(),
        )

    def to_comparable_new(p: PrescriptionCreate) -> tuple[str, str, str, str, str, str]:
        return (
            p.medication_name.strip().lower(),
            p.dose.strip().lower(),
            p.frequency.strip().lower(),
            p.duration.strip().lower(),
            str(p.route),
            (p.instructions or "").strip().lower(),
        )

    existing_set = {to_comparable_existing(p) for p in existing_prescriptions}
    new_set = {to_comparable_new(p) for p in new_prescriptions}

    return existing_set == new_set