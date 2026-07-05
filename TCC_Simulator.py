import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="保護協調模擬器", layout="wide")
st.title("⚡ 互動式電力系統保護協調模擬器")
st.markdown("操作說明：請在左側調整各保護電驛的參數，右側的 TCC 曲線將會即時重新計算並繪製。")

# --- 核心運算公式 ---
def calculate_time(I_array, Is, T, inst_I=None):
    """計算極度反時性 (EI) 曲線跳脫時間"""
    time_array = []
    for I in I_array:
        if I <= Is:
            time_array.append(None) # 不動作
        elif inst_I is not None and I >= inst_I:
            time_array.append(0.02) # 瞬時跳脫
        else:
            time = (80.0 / ((I / Is)**2 - 1)) * T
            time_array.append(time)
    return time_array

# --- 側邊欄：參數輸入區 ---
st.sidebar.header("🎛️ 參數調整盤")

st.sidebar.subheader("🔴 VCBPV-CO (相保護)")
co_is = st.sidebar.number_input("CO 啟動電流 Is (A)", value=36.0, step=1.0)
co_t = st.sidebar.slider("CO 時間倍率 T", 0.05, 1.0, 0.1, step=0.01)
co_inst = st.sidebar.number_input("CO 瞬時跳脫 I>> (A)", value=300.0, step=10.0)

st.sidebar.subheader("🟣 VCBPV-LCO (接地保護)")
lco_is = st.sidebar.number_input("LCO 啟動電流 Is (A)", value=18.0, step=1.0)
lco_t = st.sidebar.slider("LCO 時間倍率 T", 0.05, 1.0, 0.1, step=0.01)
lco_inst = st.sidebar.number_input("LCO 瞬時跳脫 I>> (A)", value=150.0, step=10.0)

st.sidebar.subheader("🔵 台電主饋線 (NX40A)")
tp_is = st.sidebar.number_input("台電 啟動電流 Is (A)", value=400.0, step=10.0)
tp_t = st.sidebar.slider("台電 時間倍率 T", 0.1, 1.0, 0.3, step=0.01)

# --- 資料準備與繪圖 ---
currents = np.logspace(0, 4, 800)
fig = go.Figure()

# 1. 加入 CO 曲線
time_co = calculate_time(currents, co_is, co_t, co_inst)
fig.add_trace(go.Scatter(x=currents, y=time_co, mode='lines', name='VCBPV-CO (相保護)', line=dict(color='red', width=2)))

# 2. 加入 LCO 曲線
time_lco = calculate_time(currents, lco_is, lco_t, lco_inst)
fig.add_trace(go.Scatter(x=currents, y=time_lco, mode='lines', name='VCBPV-LCO (接地保護)', line=dict(color='purple', width=2)))

# 3. 加入 台電 曲線
time_tp = calculate_time(currents, tp_is, tp_t)
fig.add_trace(go.Scatter(x=currents, y=time_tp, mode='lines', name='台電 NX40A', line=dict(color='cyan', width=2)))

# 4. 加入 變壓器破壞曲線 
damage_i = [252.02, 292.56, 352.48, 440.60]
damage_t = [5.0, 4.0, 3.0, 2.0]
fig.add_trace(go.Scatter(x=damage_i, y=damage_t, mode='lines+markers', name='變壓器破壞曲線', line=dict(color='orange', width=3)))

# 5. 加入 湧入電流點
fig.add_trace(go.Scatter(x=[243.09], y=[0.1], mode='markers', name='湧入電流點 (8xIn)', marker=dict(color='blue', symbol='square', size=12)))

# --- 圖表格式設定 (Log-Log 座標) ---
fig.update_layout(
    xaxis_type="log", yaxis_type="log",
    xaxis_title="電流 Current (A)", yaxis_title="時間 Time (s)",
    xaxis=dict(range=[1, 4], dtick=1, showgrid=True, gridcolor='lightgray'),
    yaxis=dict(range=[-2, 2], dtick=1, showgrid=True, gridcolor='lightgray'),
    height=700, hovermode="x unified", plot_bgcolor='white'
)

st.plotly_chart(fig, use_container_width=True)
