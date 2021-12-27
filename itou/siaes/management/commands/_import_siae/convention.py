"""

SiaeConvention object logic used by the import_siae.py script is gathered here.

"""
from django.utils import timezone

from itou.siaes.management.commands._import_siae.siae import does_siae_have_an_active_convention
from itou.siaes.management.commands._import_siae.vue_structure import ASP_ID_TO_SIRET_SIGNATURE, SIRET_TO_ASP_ID
from itou.siaes.models import Siae, SiaeConvention


def update_existing_conventions():
    """
    Update existing conventions, mainly the is_active field,
    and check data integrity on the fly.
    """
    conventions_to_deactivate = []
    reactivations = 0
    three_months_ago = timezone.now() - timezone.timedelta(days=90)

    for siae in Siae.objects.filter(source=Siae.SOURCE_ASP, convention__isnull=False).select_related("convention"):
        assert siae.siret in SIRET_TO_ASP_ID
        asp_id = SIRET_TO_ASP_ID[siae.siret]
        siret_signature = ASP_ID_TO_SIRET_SIGNATURE[asp_id]

        convention = siae.convention
        assert convention.kind == siae.kind
        assert asp_id in ASP_ID_TO_SIRET_SIGNATURE
        assert convention.siren_signature == siae.siren

        # Sometimes the same siret is attached to one asp_id in one export and to another asp_id in the next export.
        # In other words, the siae convention asp_id has changed and should be updated.
        # Ideally this should never happen because the asp_id is supposed to be an immutable id of the structure
        # in ASP data, but one can only hope.
        if convention.asp_id != asp_id:
            print(
                f"convention.id={convention.id} has changed asp_id from "
                f"{convention.asp_id} to {asp_id} (will be updated)"
            )
            assert not SiaeConvention.objects.filter(asp_id=asp_id, kind=siae.kind).exists()
            convention.asp_id = asp_id
            convention.save()
            continue

        # Siret_signature can change from one export to the next!
        # e.g. asp_id=4948 has changed from 81051848000027 to 81051848000019
        if convention.siret_signature != siret_signature:
            print(
                f"convention.id={convention.id} has changed siret_signature from "
                f"{convention.siret_signature} to {siret_signature} (will be updated)"
            )
            convention.siret_signature = siret_signature
            convention.save()

        should_be_active = does_siae_have_an_active_convention(siae)
        if convention.is_active != should_be_active:
            if should_be_active:
                # Inactive convention should be activated.
                reactivations += 1
                convention.is_active = True
                convention.save()
            elif convention.reactivated_at and convention.reactivated_at >= three_months_ago:
                # Active convention was reactivated recently by support, do not deactivate it even though it should
                # be according to latest ASP data.
                pass
            else:
                # Active convention should be deactivated.
                conventions_to_deactivate.append(convention)

    print(f"{reactivations} conventions have been reactivated")

    if len(conventions_to_deactivate) >= 100:
        # Early each year, all or most AF for the new year are missing in ASP AF data.
        # Instead of brutally deactivating all SIAE, we patiently wait until enough AF data is present.
        # While we wait, no SIAE is deactivated whatsoever.
        print(
            f"ERROR: too many conventions would be deactivated ({len(conventions_to_deactivate)})"
            f" thus none will actually be!"
        )
        return

    for convention in conventions_to_deactivate:
        convention.is_active = False
        # Start the grace period now.
        convention.deactivated_at = timezone.now()
        convention.save()
    print(f"{len(conventions_to_deactivate)} conventions have been deactivated")


def get_creatable_conventions():
    """
    Get conventions which should be created.

    Output : list of (convention, siae) tuples.
    """
    creatable_conventions = []

    for siae in Siae.objects.filter(source=Siae.SOURCE_ASP, convention__isnull=True):

        asp_id = SIRET_TO_ASP_ID.get(siae.siret)
        if asp_id not in ASP_ID_TO_SIRET_SIGNATURE:
            # Some inactive siaes are absent in the latest ASP exports but
            # are still present in db because they have members and/or job applications.
            # We cannot build a convention object for those.
            assert not siae.is_active
            continue

        siret_signature = ASP_ID_TO_SIRET_SIGNATURE.get(asp_id)

        is_active = does_siae_have_an_active_convention(siae)

        assert not SiaeConvention.objects.filter(asp_id=asp_id, kind=siae.kind).exists()

        convention = SiaeConvention(
            siret_signature=siret_signature,
            kind=siae.kind,
            is_active=is_active,
            asp_id=asp_id,
        )
        creatable_conventions.append((convention, siae))
    return creatable_conventions


def get_deletable_conventions():
    return SiaeConvention.objects.filter(siaes__isnull=True)


def check_convention_data_consistency():
    """
    Check data consistency of conventions, not only versus siaes of ASP source,
    but also vs user created siaes.
    """
    for convention in SiaeConvention.objects.prefetch_related("siaes").all():
        # Check that each active convention has exactly one siae of ASP source.
        # Unfortunately some inactive conventions have lost their ASP siae.
        asp_siaes = [siae for siae in convention.siaes.all() if siae.source == Siae.SOURCE_ASP]
        if convention.is_active:
            assert len(asp_siaes) == 1
        else:
            assert len(asp_siaes) in [0, 1]

        if not convention.is_active:
            # Check that each inactive convention has a grace period start date.
            assert convention.deactivated_at is not None

        # Additional data consistency checks.
        for siae in convention.siaes.all():
            assert siae.siren == convention.siren_signature
            if siae.kind == Siae.KIND_ACIPHC and convention.kind == SiaeConvention.KIND_ACI:
                assert siae.source == Siae.SOURCE_USER_CREATED
                # Sometimes our staff manually changes an existing ACI antenna's kind from ACI to ACIPHC and forgets
                # to detach the ACI convention.
                siae.convention = None
                siae.save()
            else:
                assert siae.kind == convention.kind

    asp_siaes_without_convention = Siae.objects.filter(
        kind__in=Siae.ASP_MANAGED_KINDS, source=Siae.SOURCE_ASP, convention__isnull=True
    ).count()
    assert asp_siaes_without_convention == 0

    user_created_siaes_without_convention = Siae.objects.filter(
        kind__in=Siae.ASP_MANAGED_KINDS,
        source=Siae.SOURCE_USER_CREATED,
        convention__isnull=True,
    ).count()
    assert user_created_siaes_without_convention == 0
