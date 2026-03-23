from src.prompts import GRAPHIC_STYLES, AGENT1_SYSTEM_PROMPT, AGENT2_SYSTEM_PROMPT, AGENT3_SYSTEM_PROMPT, AGENT4_SYSTEM_PROMPT, REFERENCE_SCRIPT

EXPECTED_STYLES = {
    "Cinematic Realism", "Anime / Ghibli", "Watercolor",
    "Graphic Novel", "Dark Fantasy", "Vintage Film",
}

def test_all_graphic_style_keys_exist():
    assert EXPECTED_STYLES == set(GRAPHIC_STYLES.keys())

def test_graphic_style_values_are_non_empty():
    for key, value in GRAPHIC_STYLES.items():
        assert value, f"Style '{key}' has empty value"

def test_agent2_prompt_has_reference_placeholder():
    assert "{reference}" in AGENT2_SYSTEM_PROMPT

def test_agent4_prompt_has_graphic_style_placeholder():
    assert "{graphic_style}" in AGENT4_SYSTEM_PROMPT

def test_prompts_format_without_error():
    AGENT2_SYSTEM_PROMPT.format(reference=REFERENCE_SCRIPT)
    AGENT4_SYSTEM_PROMPT.format(graphic_style="cinematic realism, test")
