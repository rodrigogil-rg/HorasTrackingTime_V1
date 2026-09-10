from src.excel_writer import sanitize_filename, sanitize_sheet_name


def test_sanitize_sheet_name():
    existing = {"Resumen general"}
    assert sanitize_sheet_name("Cliente A", existing) == "Cliente A"
    existing.add("Cliente A")
    assert sanitize_sheet_name("Cliente A", existing) == "Cliente A_2"
    assert sanitize_sheet_name("Cliente/Con:Barras", existing) == "Cliente_Con_Barras"

    # Max 31 chars test
    long_name = "A" * 40
    sanitized = sanitize_sheet_name(long_name, set())
    assert len(sanitized) <= 31


def test_sanitize_filename():
    assert sanitize_filename("Rodrigo Gil") == "Rodrigo_Gil"
    assert sanitize_filename("Test / Name*?:") == "Test___Name___"
