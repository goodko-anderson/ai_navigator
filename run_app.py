import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # 指向您真正的 streamlit 主程式檔案
    main_script = resolve_path("your_main_script.py") 
    
    # 模擬命令行啟動
    sys.argv = [
        "streamlit",
        "run",
        main_script,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())