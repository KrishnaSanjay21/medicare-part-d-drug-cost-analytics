from streamlit.testing.v1 import AppTest


def test_all_dashboard_views_render_without_exceptions():
    app = AppTest.from_file("streamlit_app.py").run(timeout=30)
    assert not app.exception

    for page in ["Drug Analysis", "State Comparison", "Data Quality & Methodology"]:
        app.sidebar.radio[0].set_value(page)
        app.run(timeout=30)
        assert not app.exception

