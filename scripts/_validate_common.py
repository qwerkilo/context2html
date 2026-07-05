"""Shared validation helpers — barrel re-export from framework package."""

from context2html.validator.common import (
    PASS, FAIL,
    check_h1_count, check_relative_links,
    check_focus_visible, check_tabular_nums,
    check_semantic_html, check_lib_deps, check_bilingual,
    check_cross_refs, check_data_anim_syntax, check_gsap_modes,
)
from context2html.validator.svg import check_svg_links, check_svg_contrast
