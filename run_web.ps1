Set-Location -LiteralPath $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\python.exe" -m streamlit run "$PSScriptRoot\streamlit_app.py" --server.address=127.0.0.1 --server.port=8501
