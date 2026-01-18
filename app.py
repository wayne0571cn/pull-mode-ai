import streamlit as st
import importlib.util
import os

# 1. 页面配置
st.set_page_config(page_title="AI 插件工作站", page_icon="🧩", layout="wide")

# 2. 权限门禁
ACCESS_PASSWORD = "123" 
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.get("pwd_input") == ACCESS_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.error("密码错误")

if not st.session_state.authenticated:
    st.title("🔐 AI 工作站入口")
    st.text_input("输入访问密码", type="password", key="pwd_input", on_change=check_password)
    st.stop()

# 3. 插件加载引擎
def load_plugins():
    plugins = {}
    plugin_dir = "plugins"
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
    
    files = [f for f in os.listdir(plugin_dir) if f.endswith(".py")]
    for file in sorted(files):
        module_name = file[:-3]
        file_path = os.path.join(plugin_dir, file)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "TITLE") and hasattr(module, "run"):
            plugins[module.TITLE] = module.run
    return plugins

# 4. 侧边栏与渲染
all_plugins = load_plugins()
st.sidebar.title("🧩 插件菜单")
if all_plugins:
    choice = st.sidebar.radio("请选择功能模块：", list(all_plugins.keys()))
    st.sidebar.divider()
    all_plugins[choice]() # 运行对应插件
else:
    st.sidebar.warning("请在 plugins 文件夹下添加插件文件")