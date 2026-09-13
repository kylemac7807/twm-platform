#!/usr/bin/env bash
# TWM corpus fetcher — run from a machine with normal internet access.
# All URLs verified on official issuer sites on 2026-09-01 (see manifest.md).
set -u
cd "$(dirname "$0")"
get() { # get <output-name> <url>
  echo "== $1"
  curl -fL --retry 2 -o "$1" "$2" || echo "FAILED: $2"
}

# --- O*NET 31.0 (CC BY 4.0) ---
B="https://www.onetcenter.org/dl_files/database"
get ONET_31.0_full_excel.zip            "$B/db_31_0_excel.zip"
get ONET_31.0_Occupation_Data.xlsx      "$B/db_31_0_excel/Occupation%20Data.xlsx"
get ONET_31.0_Job_Titles.xlsx           "$B/db_31_0_excel/Job%20Titles.xlsx"
get ONET_31.0_Sample_Reported_Titles.xlsx "$B/db_31_0_excel/Sample%20of%20Reported%20Titles.xlsx"
get ONET_31.0_Essential_Skills.xlsx     "$B/db_31_0_excel/Essential%20Skills.xlsx"
get ONET_31.0_Transferable_Skills.xlsx  "$B/db_31_0_excel/Transferable%20Skills.xlsx"
get ONET_31.0_Software_Skills.xlsx      "$B/db_31_0_excel/Software%20Skills.xlsx"

# --- NICE / NIST (public domain) ---
get NIST_SP800-181r1_NICE_Framework.pdf "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-181r1.pdf"
get NICE_Framework_Components_v2.2.0.json "https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/v2-2-0_nf_components.json"
echo "NOTE: NICE components XLSX — follow link on https://www.nist.gov/document/nice-framework-components-v220"

# --- UK Government Digital and Data / DDaT (OGL v3.0) ---
echo "NOTE: DDaT CSV export links are timestamped and rotate."
echo "      Grab current 'Role and skill content' + 'Skills Content' CSVs from:"
echo "      https://ddat-capability-framework.service.gov.uk/download"

# --- ENISA ECSF ---
get ENISA_ECSF_Role_Profiles.pdf "https://www.enisa.europa.eu/sites/default/files/publications/European%20Cybersecurity%20Skills%20Framework%20Role%20Profiles.pdf"

# --- CEN CWA 16458 ICT role profiles (free CWAs) ---
C="https://www.cencenelec.eu/media/CEN-CENELEC/AreasOfWork/CEN%20sectors/Digital%20Society/CWA%20Download%20Area/ICT_SkillsWS"
get CEN_CWA16458-1_2018_ICT_Role_Profiles.pdf "$C/16458-1.pdf"
get CEN_CWA16458-2_User_Guides.pdf            "$C/16458-2.pdf"
get CEN_CWA16458-4_Case_Studies.pdf           "$C/16458-4.pdf"

# --- Singapore SFw for ICT (IMDA) ---
get SG_SFw_ICT_Consolidated_Career_Maps.pdf "https://www.imda.gov.sg/-/media/imda/images/programmes/skills-framework-for-ict/consolidated-career-maps.pdf"

# --- Manual steps (login/email-gated; see manifest.md section B) ---
echo "MANUAL: SFIA 9 PDF/Excel/RDF — free registration at https://sfia-online.org/en/sfia-9/documentation"
echo "MANUAL: ESCO v1.2.1 CSV — email flow at https://esco.ec.europa.eu/en/use-esco/download"

# --- Verify ---
echo; echo "== Verification =="
for f in *.pdf *.xlsx *.zip *.json *.csv; do [ -f "$f" ] && file "$f"; done
for f in *.pdf; do [ -f "$f" ] && { echo "--- $f"; pdftotext "$f" - 2>/dev/null | head -5; }; done
