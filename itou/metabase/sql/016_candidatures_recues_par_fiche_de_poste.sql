/* 
 
L'objectif est d'analyser les candidatures qui sont reliées à une fiche de poste dans le but de détécter celles qui ont
des difficultés à recruter.

*/

select 
    c.date_candidature,
    c.date_embauche,
    c."délai_de_réponse",
    (current_date - c.date_candidature) as anciennete_candidature,
    (current_date - fdp."date_création") as delai_mise_en_ligne,
    (date_embauche - date_candidature) as delai_embauche, /* nous donne une date en jours */
    c."délai_prise_en_compte",
    c."département_structure",
    c.id as id_candidature,
    /* TODO dejafait drop as soon as analistos have migrated to the new deanonymized column */
    c."id_anonymisé" as "id_candidature_anonymisé",
    c.id_candidat,
    /* TODO dejafait drop as soon as analistos have migrated to the new deanonymized column */
    c."id_candidat_anonymisé" as "id_candidat_anonymisé",
    c.id_structure,
    c.motif_de_refus,
    c."nom_département_structure",
    c.nom_org_prescripteur,
    c.id_org_prescripteur,
    "o.nom_département as nom_département_prescripteur",
    c.nom_structure,
    c.origine as origine_candidature,
    c."origine_détaillée" as "origine_détaillée_candidature",
    c."région_structure",
    c.safir_org_prescripteur,
    c.type_structure,
    c."état" as "état_candidature",
    fdp.recrutement_ouvert as recrutement_ouvert_fdp,
    crdp.grand_domaine,
    crdp.domaine_professionnel,
    fdp.code_rome as code_rome_fpd,
    fdp."date_création" as "date_création_fdp",
    fdp."date_mise_à_jour_metabase",
    fdp.id as id_fdp,
    fdp.nom_rome as nom_rome_fdp,
    fdp.id_employeur,
    fdp.siret_employeur,
    c.injection_ai
from 
    candidatures c 
left join
    organisations o     
    on o.id = c.id_org_prescripteur
inner join 
    fiches_de_poste_par_candidature fdppc 
    on c.id = fdppc.id_candidature 
inner join 
    fiches_de_poste fdp 
    on fdp.id = fdppc.id_fiche_de_poste
inner join 
    code_rome_domaine_professionnel as crdp 
    on fdp.code_rome = crdp.code_rome 
