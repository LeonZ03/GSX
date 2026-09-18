# Evidence file review

Reviewed 2026-09-18 against the archived Suzuki catalogue `raw/suzuki_GSX250RAM1_GSX250RAZM1.pdf`. Page numbers below use the PDF viewer's zero-based page labels returned by the official PDF text extraction (`Pxx`); add one for a conventional one-based PDF page number.

## Part-number verification

- `44100-20K00-W6B` is an exact line item in FIG.420A FUEL TANK, `P57-58`, described as the blue tank assembly for body colour BY7.
- `44191-20K00` is an exact line item in FIG.420A, `P57-58`, described as the fuel-tank centre cover.
- `35100-20K01` is an exact line item in FIG.333A HEADLAMP, `P46-47`, described as the headlamp assembly.
- `94461-20K00` and `94462-20K00` are exact line items in FIG.485A SIDE COWLING, `P79`, described as inner right/left cowlings.
- `94475-20K00-YAY` and `94485-20K00-YAY` are exact line items in FIG.485A, `P79`, described as black right/left side cowlings for the YAY colour variant.
- `94481-20K00` is an exact line item in FIG.485A, `P79`, described as the under-cowling left component.
- `45100-20K01-QFE` and `45300-20K01-QFE` are exact line items in FIG.505A SEAT, `P85-86`, described as black rider and pillion seat assemblies.

The JSON's listed part numbers therefore match the catalogue text. The colour suffixes are catalogue variant data; they are not assertions that the owner's blue motorcycle uses the YAY black replacement panels.

## Specification cross-check

The Haojue official page states 1430 mm wheelbase, 290 mm front disc, 240 mm rear disc, and 110/80-17 M/C 57H front plus 140/70-17 M/C 66H rear. Those values are transcribed in `evidence.json` without conversion. The page also states 2085 x 740 x 1110 mm, 790 mm seat height and 15 L tank capacity.

## Official turntable imagery limitation

Existing official turntable images in `references/public` can support broad silhouette, component placement and colour blocking. They are ordinary perspective views with lens distortion and unknown camera parameters, not orthographic or calibrated projection. They must not be used to infer exact cross-section, hidden mounting coordinates, or millimetre geometry; owner photographs remain the appearance authority.
