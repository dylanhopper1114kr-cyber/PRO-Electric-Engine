import streamlit as st
import math
import re
from typing import Dict, List, Tuple, Any, Optional

# ==========================================
# 0. 網頁基本設定與頁面排版
# ==========================================
st.set_page_config(page_title="單線圖直式審查系統", page_icon="⚡", layout="wide")

# ==========================================
# 1. 高精準度導線阻抗全局對照資料庫 (去太陽能版)
# ==========================================
GLOBAL_R_PVC_DB: Dict[str, float] = {
    '1.6_單線': 10.8, '2.0_單線': 6.85, '2.0_絞線': 11.21, '2.0': 11.21, '2.6': 4.20,
    '3.5': 6.32, '5.5': 4.01, '8': 2.82, '14': 1.57, '22': 1.0,
    '30': 0.745, '38': 0.591, '50': 0.484, '60': 0.378, '80': 0.279, '100': 0.223,
    '125': 0.18, '150': 0.152, '200': 0.115, '250': 0.094, '325': 0.073,
    '400': 0.061, '500': 0.05
}

GLOBAL_R_XLPE_DB: Dict[str, float] = {
    '1.6_單線': 11.3, '2.0_單線': 7.2, '2.0_絞線': 11.76, '2.0': 11.76, '2.6': 4.40,
    '3.5': 6.63, '5.5': 4.21, '8': 2.96, '14': 1.65, '22': 1.05,
    '30': 0.835, '38': 0.62, '50': 0.508, '60': 0.397, '80': 0.293, '100': 0.235,
    '125': 0.189, '150': 0.161, '200': 0.122, '250': 0.1, '325': 0.078,
    '400': 0.066, '500': 0.055
}

GLOBAL_X_DB: Dict[str, float] = {
    '1.6_單線': 0.128, '2.0_單線': 0.122, '2.0_絞線': 0.125, '2.0': 0.125, '2.6': 0.120,
    '3.5': 0.118, '5.5': 0.115, '8': 0.113, '14': 0.109, '22': 0.105,
    '30': 0.103, '38': 0.101, '50': 0.099, '60': 0.098, '80': 0.096, '100': 0.095,
    '125': 0.094, '150': 0.093, '200': 0.091, '250': 0.09, '325': 0.088,
    '400': 0.087, '500': 0.086
}

TX_IMPEDANCE_DB: Dict[float, Tuple[float, float]] = {
    5.0: (2.60, 3.04), 10.0: (2.20, 2.50), 30.0: (1.92, 1.45), 50.0: (1.80, 2.00),
    100.0: (1.60, 2.50), 150.0: (1.50, 3.00), 167.0: (1.20, 1.96), 200.0: (1.40, 3.50),
    300.0: (1.30, 4.00), 500.0: (1.20, 4.50), 501.0: (1.20, 1.96), 750.0: (1.10, 4.80),
    1000.0: (1.00, 4.90), 1500.0: (0.90, 5.50), 2000.0: (0.80, 6.00)
}

DB_TABLE_25_4: Dict[str, List[int]] = {
    '1.6': [24, 21, 19, 17], '2.0': [28, 25, 22, 20], '2.6': [39, 35, 31, 27],
    '3.5': [30, 27, 24, 21], '5.5': [39, 35, 31, 27], '8': [51, 46, 41, 36],
    '14': [74, 67, 59, 52], '22': [93, 84, 74, 65], '30': [116, 104, 93, 81],
    '38': [130, 117, 104, 91], '50': [155, 140, 124, 109], '60': [176, 158, 141, 123],
    '80': [208, 187, 166, 146], '100': [241, 217, 193, 169], '125': [276, 248, 221, 193],
    '150': [308, 277, 246, 0], '200': [358, 322, 286, 0], '250': [412, 371, 0, 0],
    '325': [469, 422, 0, 0], '400': [530, 0, 0, 0], '500': [579, 0, 0, 0]
}

DB_TABLE_25_5: Dict[str, List[int]] = {
    '1.6': [13, 12, 10, 9], '2.0': [18, 16, 14, 12], '2.6': [24, 22, 19, 16],
    '3.5': [19, 16, 14, 12], '5.5': [25, 23, 20, 17], '8': [33, 30, 25, 20],
    '14': [50, 40, 35, 30], '22': [60, 55, 50, 40], '30': [75, 65, 55, 50],
    '38': [85, 75, 65, 55], '50': [100, 90, 80, 65], '60': [115, 105, 90, 75],
    '80': [140, 125, 105, 90], '100': [160, 150, 125, 105], '125': [185, 165, 140, 125],
    '150': [215, 190, 165, 0], '200': [251, 225, 200, 0], '250': [292, 263, 0, 0],
    '325': [330, 297, 0, 0], '400': [373, 0, 0, 0], '500': [409, 0, 0, 0]
}

BUSWAY_DB: Dict[str, float] = {
    "15x2 (1組)": 130.0, "15x3 (1組)": 155.0, "20x2 (1組)": 175.0, "20x3 (1組)": 220.0, "20x5 (1組)": 285.0,
    "25x3 (1組)": 250.0, "25x5 (1組)": 325.0, "30x3 (1組)": 305.0, "30x5 (1組)": 370.0, "30x5 (2組)": 670.0,
    "40x5 (1組)": 420.0, "40x5 (2組)": 800.0, "40x10 (1組)": 715.0, "40x10 (2組)": 1230.0, "50x5 (1組)": 585.0,
    "50x5 (2組)": 1030.0, "50x10 (1組)": 875.0, "50x10 (2組)": 1600.0, "60x5 (1組)": 700.0, "60x5 (2組)": 875.0,
    "60x10 (1組)": 1000.0, "60x10 (2組)": 1790.0, "60x10 (3組)": 2540.0, "80x10 (1組)": 1300.0, "80x10 (2組)": 2240.0,
    "80x10 (3組)": 3310.0, "80x10 (4組)": 4250.0, "100x10 (1組)": 1650.0, "100x10 (2組)": 1735.0, "100x10 (3組)": 3770.0,
    "120x10 (1組)": 1920.0, "120x10 (2組)": 3100.0, "120x10 (3組)": 4000.0
}

def get_num(v: Any) -> float:
    if v is None or (isinstance(v, float) and math.isnan(v)): return 0.0
    m = re.search(r"[-+]?\d*\.?\d+", str(v))
    return float(m.group()) if m else 0.0

def get_actual_wire_area(w_type: str, w_ins: str, w_size: str) -> float:
    try: sz = float(w_size)
    except ValueError: return 0.0
    if w_type == '單芯線':
        if math.isclose(sz, 1.6): return 9.6
        if math.isclose(sz, 2.0): return 12.6
        if math.isclose(sz, 2.6): return 16.6
    else:
        if 'XLPE' in w_ins:
            xlpe_map = {5.5: 28.2743, 8: 38.4845, 14: 56.745, 22: 78.5398, 30: 95.0332, 38: 113.0973, 50: 147.4114, 60: 165.13, 80: 201.0619, 100: 240.5282, 125: 298.6477, 150: 346.3606, 200: 433.7361, 250: 551.5459, 325: 706.8583, 400: 850.0, 500: 1000.0}
            for k, v in xlpe_map.items():
                if math.isclose(sz, k): return v
        else:
            pvc_map = {2: 10.1788, 3.5: 12.5664, 5.5: 19.635, 8: 28.2743, 14: 45.3646, 22: 66.4761, 30: 86.5901, 38: 103.8689, 50: 132.7323, 60: 153.938, 80: 188.6919, 100: 226.9801, 150: 346.3606, 200: 415.4756, 250: 510.7052, 325: 706.8583, 400: 850.0, 500: 1000.0}
            for k, v in pvc_map.items():
                if math.isclose(sz, k): return v
    return 22.0

def get_rx_values(wire_size: str, wire_type: str, ins_type: str) -> Tuple[float, float]:
    wire_key = str(wire_size).strip()
    if wire_key == '2.0':
        wire_key = '2.0_單線' if '單' in wire_type else '2.0_絞線'
    if 'XLPE' in ins_type:
        r_val = GLOBAL_R_XLPE_DB.get(wire_key, GLOBAL_R_XLPE_DB.get(str(wire_size).strip(), 1.30))
    else:
        r_val = GLOBAL_R_PVC_DB.get(wire_key, GLOBAL_R_PVC_DB.get(str(wire_size).strip(), 1.30))
    x_val = GLOBAL_X_DB.get(wire_key, GLOBAL_X_DB.get(str(wire_size).strip(), 0.13))
    return r_val, x_val

# ==========================================
# 2. 核心圖審審查與公式直式展開引擎 (回傳 HTML 字串)
# ==========================================
def design_ai(cdata: Dict[str, Any], cir_id_name: str, db: Dict[str, Any]) -> str:
    if '受電盤' in cir_id_name or '錶箱' in cir_id_name: cir = '進屋線/變壓器二次側'
    elif '次幹線' in cir_id_name: cir = '分路'
    elif '幹線' in cir_id_name or 'MP總' in cir_id_name: cir = '幹線'
    else: cir = '分路'

    ph = str(cdata.get('ph', '無'))
    kw = get_num(cdata.get('kw', 0.0))
    vol = get_num(cdata.get('vol', 0.0))
    pf = get_num(cdata.get('pf', 0.0))
    length = get_num(cdata.get('length', 0.0))
    up_name = str(cdata.get('up', '無'))
    nfb = get_num(cdata.get('nfb', 0.0))
    ins = str(cdata.get('ins', '無'))
    wire_type = str(cdata.get('wire_type', '無'))
    wire = str(cdata.get('wire', '無')).strip()
    try: w_cnt_int = int(cdata.get('cnt', 0))
    except: w_cnt_int = 0

    pipe_opt = str(cdata.get('pipe_opt', '無'))
    busway_spec = str(cdata.get('busway', '無'))
    d_s = str(cdata.get('ds', '無'))
    g_type = str(cdata.get('gtype', '無'))
    gw = str(cdata.get('gw', '無')).strip()
    gr = get_num(cdata.get('gr', 0.0))
    ic_ka = get_num(cdata.get('ic', 0.0))
    loc = str(cdata.get('loc', '無'))
    kvar = get_num(cdata.get('kvar', 0.0))
    base_kva = get_num(cdata.get('base_kva', 1000.0))
    if base_kva <= 0: base_kva = 1000.0
    k_factor = get_num(cdata.get('k_factor', 1.01))

    is_capacitor = ('電容' in cir_id_name)
    is_high_voltage = (vol >= 1000.0)

    # 一、 負載電流
    if is_capacitor:
        vol_f = (1.73205 * vol) if '三相' in ph else vol
        calc_c = round((kvar * 1000) / vol_f, 2) if vol_f > 0 else 0.0
        formula_text = f"I_line = (kVAR × 1000) / ({'√3 × ' if '三相' in ph else ''}V)"
        substitution_text = f"I_line = ({kvar} × 1000) / ({'1.73205 × ' if '三相' in ph else ''}{vol}V) = {calc_c} A"
    else:
        vol_f = (1.73205 * vol * pf) if '三相' in ph else (vol * pf)
        calc_c = round((kw * 1000) / vol_f, 2) if vol_f > 0 else 0.0
        formula_text = f"I = (kW × 1000) / ({'√3 × ' if '三相' in ph else ''}V × PF)"
        substitution_text = f"I = ({kw} × 1000) / ({'1.73205 × ' if '三相' in ph else ''}{vol}V × {pf}) = {calc_c} A"

    # 二、 斷路器與導線安培容量
    nst = "✅ OK" if nfb >= calc_c else f"❌ NG"
    nfb_txt = f"過電流保護裝置額定 (NFB: {nfb}A) ≥ 負載計算電流 ({calc_c}A)"
    
    wst_txt = "✅ OK"
    if wire_type == '無' or wire == '無':
        wire_html_detail = "&nbsp;&nbsp;• <b>法規協調</b>：未配置實體導線，免執行查表與降容審查。"
    else:
        ins_t = 90 if 'XLPE' in ins else 60
        pipe_t = 60 if 'PVC' in pipe_opt else 90
        eval_t = min(ins_t, pipe_t)
        
        idx = 0 if w_cnt_int <= 3 else (1 if w_cnt_int == 4 else (2 if w_cnt_int <= 6 else 3))
        chosen_db, table_title = (DB_TABLE_25_4, "表 25-4 (XLPE 90℃基準)") if eval_t >= 90 else (DB_TABLE_25_5, "表 25-5 (PVC 60℃降容基準)")
        c_amp = chosen_db.get(wire, [0, 0, 0, 0])[idx] if idx < len(chosen_db.get(wire, [0, 0, 0, 0])) else 0
        
        if c_amp == 0 or c_amp < calc_c or c_amp < nfb: wst_txt = "❌ NG"
        
        wire_html_detail = (
            f"&nbsp;&nbsp;• <b>查表依據</b>：【{table_title}】 / 配管: {pipe_opt}<br>"
            f"&nbsp;&nbsp;• <b>參數帶入</b>：線徑 {wire} mm² / 載流導線數 {w_cnt_int} 根 ➜ 容許安培容量 = <b>{c_amp} A</b><br>"
            f"&nbsp;&nbsp;• <b>法規協調</b>：安培容量 ({c_amp}A) ≥ NFB 額定 ({nfb}A) 且 ≥ 負載電流 ({calc_c}A) ➜ <span style='font-weight:bold; color:{'#16a34a' if 'OK' in wst_txt else '#dc2626'}'>{wst_txt}</span>"
        )

    # 三、 電壓降
    def get_node_vd(n_name, n_ph, n_kw, n_vol, n_pf, n_len, n_wire, n_type, n_ins):
        if n_type == '無' or n_wire == '無' or '電容' in n_name or n_len <= 0: return 0.0, "免計"
        n_vf = (1.73205 * n_vol * n_pf) if '三相' in n_ph else (n_vol * n_pf)
        n_i = (n_kw * 1000) / n_vf if n_vf > 0 else 0.0
        n_r, n_x = get_rx_values(n_wire, n_type, n_ins)
        n_sin = math.sqrt(1 - n_pf**2) if n_pf <= 1 else 0.0
        n_kv = 2.0 if ('單相' in n_ph and ('二' in n_ph or '兩' in n_ph)) else (1.0 if ('單相三' in n_ph or '三相四' in n_ph) else 1.73205)
        
        v_drop = (n_kv * n_i * n_len * (n_r * n_pf + n_x * n_sin)) / 1000
        vd_pct = round((v_drop / n_vol) * 100, 2) if n_vol > 0 else 0.0
        expr = f"ΔV = {n_kv:.3f} × {n_i:.2f}A × ({n_len}m/1000) × ({n_r}×{n_pf} + {n_x}×{n_sin:.3f}) = {v_drop:.2f}V ➜ <b>{vd_pct}%</b>"
        return vd_pct, expr

    def get_cum_vd_detail(c_name, visited=None):
        if visited is None: visited = set()
        if not db or c_name not in db or c_name == '無' or c_name in visited: return 0.0, []
        visited.add(c_name)
        node = db[c_name]
        v_pct, expr_str = get_node_vd(
            c_name, str(node.get('ph', '無')), get_num(node.get('kw', 0.0)), get_num(node.get('vol', 0.0)),
            get_num(node.get('pf', 0.0)), get_num(node.get('length', 0.0)), str(node.get('wire', '無')),
            str(node.get('wire_type', '無')), str(node.get('ins', '無'))
        )
        up_vd, up_path = get_cum_vd_detail(node.get('up', '無'), visited)
        return v_pct + up_vd, up_path + [(c_name, v_pct, expr_str)]

    cur_vd_pct, cur_expr = get_node_vd(cir_id_name, ph, kw, vol, pf, length, wire, wire_type, ins)
    up_vd_pct, up_path = get_cum_vd_detail(up_name)
    total_vd_pct = round(cur_vd_pct + up_vd_pct, 2)
    vd_limit = 3.0 if cir in ['幹線', '進屋線/變壓器二次側'] else 2.0
    vd_st = "✅ OK" if cur_vd_pct <= vd_limit and total_vd_pct <= 5.0 else "❌ NG"

    vd_cascade_html = "".join([f"&nbsp;&nbsp;&nbsp;&nbsp;↳ [上游段 {n}]: {e}<br>" for n, v, e in reversed(up_path) if "免計" not in e])
    vd_cascade_html += f"&nbsp;&nbsp;&nbsp;&nbsp;↳ [當前本段 {cir_id_name}]: {cur_expr}<br>"

    if '單相' in ph and ('二' in ph or '兩' in ph): vd_formula_str = "ΔV = 2 × I × (L/1000) × (R×cosθ + X×sinθ)"
    elif '單相三' in ph or '三相四' in ph: vd_formula_str = "ΔV = 1 × I × (L/1000) × (R×cosθ + X×sinθ)"
    else: vd_formula_str = "ΔV = √3 × I × (L/1000) × (R×cosθ + X×sinθ)"

    vd_html_detail = (
        f"&nbsp;&nbsp;• <b>直式公式</b>：<code style='font-size:13px; color:#b91c1c; font-weight:bold;'>{vd_formula_str}</code><br>"
        f"&nbsp;&nbsp;• <b>級聯數值代入分解：</b><br>{vd_cascade_html}"
        f"&nbsp;&nbsp;• <b>法規協調 (單段)</b>：當前段壓降 ({cur_vd_pct}%) ≤ 單段限制 ({vd_limit}%)<br>"
        f"&nbsp;&nbsp;• <b>法規協調 (累計)</b>：累計總壓降 ({total_vd_pct}%) ≤ 總限制 (5.0%) ➜ <span style='font-weight:bold; color:{'#16a34a' if 'OK' in vd_st else '#dc2626'}'>{vd_st}</span>"
    )

    # 四、 法定最低 ICU
    if vol == 11400: sys_key = "高壓11.4kV"
    elif vol == 22800: sys_key = "高壓22.8kV"
    else: sys_key = "單相110V/220V" if "單相" in ph else ("三相220V" if vol <= 220 else "三相380V")

    ic_db = {
        "單相110V/220V": {"受電箱": [(75, 35, "75A 以下"), (100, 35, "100A 以下"), (float('inf'), 35, "超過 100A")], "集中(單獨)表箱": [(75, 20, "75A 以下"), (100, 20, "100A 以下"), (float('inf'), 25, "超過 100A")], "用戶總開關箱": [(75, 10, "75A 以下"), (100, 15, "100A 以下"), (float('inf'), 20, "超過 100A")]},
        "三相220V": {"受電箱": [(75, 35, "75A 以下"), (200, 35, "200A 以下"), (float('inf'), 35, "超過 200A")], "集中(單獨)表箱": [(75, 20, "75A 以下"), (200, 20, "200A 以下"), (float('inf'), 25, "超過 200A")], "用戶總開關箱": [(75, 10, "75A 以下"), (200, 15, "200A 以下"), (float('inf'), 20, "超過 200A")]},
        "三相380V": {"受電箱": [(75, 35, "75A 以下"), (200, 35, "200A 以下"), (float('inf'), 35, "超過 200A")], "集中(單獨)表箱": [(75, 25, "75A 以下"), (200, 25, "200A 以下"), (float('inf'), 30, "超過 200A")], "用戶總開關箱": [(75, 15, "75A 以下"), (200, 20, "200A 以下"), (float('inf'), 25, "超過 200A")]},
        "高壓11.4kV": {"受電箱": [(float('inf'), 12.5, "高壓總保護")], "集中(單獨)表箱": [(float('inf'), 12.5, "高壓總保護")], "用戶總開關箱": [(float('inf'), 12.5, "高壓總保護")]},
        "高壓22.8kV": {"受電箱": [(float('inf'), 25.0, "高壓總保護")], "集中(單獨)表箱": [(float('inf'), 25.0, "高壓總保護")], "用戶總開關箱": [(float('inf'), 25.0, "高壓總保護")]}
    }
    loc_key = loc.replace("(Main)", "").replace("(Sub)", "").strip()
    target_ic, limit_msg = 10, "查無級距"
    try:
        for limit, val, msg in ic_db[sys_key][loc_key]:
            if nfb <= limit: target_ic, limit_msg = val, msg; break
    except: pass
    ic_st = "✅ OK" if ic_ka >= target_ic else f"❌ NG"
    
    ic_html_detail = (
        f"&nbsp;&nbsp;• <b>查表依據</b>：【表五八】 / 環境 {sys_key} / 位置 {loc_key} / NFB級距 {limit_msg}<br>"
        f"&nbsp;&nbsp;• <b>法規協調</b>：選用開關 IC ({ic_ka} kA) ≥ 法定最低要求 ({target_ic} kA) ➜ <span style='font-weight:bold; color:{'#16a34a' if 'OK' in ic_st else '#dc2626'}'>{ic_st}</span>"
    )

    # 五、 系統故障電流
    def get_cum_z_pu_detail(c_name, visited=None):
        if visited is None: visited = set()
        if not db or c_name not in db or c_name == '無' or c_name in visited: return complex(0, 0), []
        visited.add(c_name)
        node = db[c_name]
        up_z, up_path = get_cum_z_pu_detail(node.get('up', '無'), visited)

        n_tpc_mva = get_num(node.get('tpc_mva', 0.0))
        n_tx_kva = get_num(node.get('tx_kva', 0.0))
        cur_src_r, cur_src_x = 0.0, 0.0
        src_msg_list = []

        if n_tpc_mva > 0:
            z_tpc_mag = (base_kva / 1000.0) / n_tpc_mva
            r_tpc = z_tpc_mag / math.sqrt(1 + 25**2)
            x_tpc = 25 * r_tpc
            cur_src_r += r_tpc
            cur_src_x += x_tpc
            src_msg_list.append(f"Z_TPC({n_tpc_mva}MVA換算)={r_tpc:.5f}+j{x_tpc:.5f}")

        if n_tx_kva > 0:
            tx_r = get_num(node.get('tx_pct_r', 0.0))
            tx_x = get_num(node.get('tx_pct_x', 0.0))
            r_tr_pu = (tx_r / 100.0) * (base_kva / n_tx_kva)
            x_tr_pu = (tx_x / 100.0) * (base_kva / n_tx_kva)
            cur_src_r += r_tr_pu
            cur_src_x += x_tr_pu
            src_msg_list.append(f"Z_TR({n_tx_kva}kVA換底)={r_tr_pu:.5f}+j{x_tr_pu:.5f}")

        src_z = complex(cur_src_r, cur_src_x)
        n_vol_kv = get_num(node.get('vol', 0)) / 1000.0
        n_len = get_num(node.get('length', 0.0))
        n_wire = str(node.get('wire', '無')).strip()
        n_wire_type = str(node.get('wire_type', '無'))
        n_ins = str(node.get('ins', '無'))

        if n_wire_type == '無' or n_wire == '無' or n_len <= 0:
            cur_cable_z = complex(0, 0)
            cable_msg = "無線路阻抗"
        else:
            z_base_n = (n_vol_kv**2) * 1000 / base_kva if base_kva > 0 else 1.0
            r_val, x_val = get_rx_values(n_wire, n_wire_type, n_ins)
            r_ohm_c = r_val * (n_len / 1000.0)
            x_ohm_c = x_val * (n_len / 1000.0)
            r_pu = r_ohm_c / z_base_n if z_base_n > 0 else 0.0
            x_pu = x_ohm_c / z_base_n if z_base_n > 0 else 0.0
            cur_cable_z = complex(r_pu, x_pu)
            cable_msg = f"Z_cable({n_len}m 實體 R={r_ohm_c:.4f}Ω, X={x_ohm_c:.4f}Ω) ➜ 換算 pu = {r_pu:.5f}+j{x_pu:.5f}"

        total_node_z = src_z + cur_cable_z
        combined_desc = " ＋ ".join(src_msg_list + [cable_msg])
        return up_z + total_node_z, up_path + [(c_name, up_z + total_node_z, combined_desc)]

    z_total, sc_path = get_cum_z_pu_detail(cir_id_name)
    z_mag = abs(z_total)
    vol_kv = vol / 1000.0
    phase_factor = 1.73205 if '三相' in ph else 1.0
    i_base = base_kva / (phase_factor * vol_kv) if vol_kv > 0 else 0.0
    i_sym = (i_base / z_mag) / 1000.0 if z_mag > 0 else 0.0
    i_asym = i_sym * k_factor
    fc_ok = ic_ka >= i_asym
    fc_st = "✅ OK" if fc_ok else "❌ NG"

    sc_cascade_html = "".join([f"&nbsp;&nbsp;• [路徑節點 {n} 向量公式]:<br>&nbsp;&nbsp;&nbsp;&nbsp;↳ {d}<br>&nbsp;&nbsp;&nbsp;&nbsp;↳ 累計阻抗 ΣZ = <b>{z.real:.5f} + j{z.imag:.5f} pu</b> (大小 |Z| = {abs(z):.5f})<br>" for n, z, d in sc_path])

    # 六、 匯流排與線槽空間占比檢討
    busway_rating_ac = BUSWAY_DB.get(busway_spec, 0.0) if busway_spec != '無' else 0.0
    bst = "✅ OK" if busway_spec == '無' or busway_rating_ac >= nfb else "❌ NG"
    
    if busway_spec == '無':
        busway_html = "&nbsp;&nbsp;• <b>法規協調</b>：未選用匯流排，免計容量。"
    else:
        busway_html = (
            f"&nbsp;&nbsp;• <b>參數帶入</b>：選用 {busway_spec} ➜ 容許安培容量 = <b>{busway_rating_ac} A</b><br>"
            f"&nbsp;&nbsp;• <b>法規協調</b>：匯流排容許安培容量 ({busway_rating_ac}A) ≥ NFB額定 ({nfb}A) ➜ <span style='font-weight:bold; color:{'#16a34a' if 'OK' in bst else '#dc2626'}'>{bst}</span>"
        )

    twa, rt_d, rst_d = 0.0, 0.0, "✅ OK"
    if d_s != '無' and wire_type != '無' and wire != '無' and w_cnt_int > 0:
        single_wa = get_actual_wire_area(wire_type, ins, wire)
        twa = single_wa * w_cnt_int
        try:
            w_tray, h_tray = map(float, d_s.lower().split('x'))
            tray_area = w_tray * h_tray
            rt_d = round((twa / tray_area) * 100, 1) if tray_area > 0 else 0.0
            rst_d = "✅ OK" if rt_d <= 20.0 else "❌ NG"
            tray_html = (
                f"&nbsp;&nbsp;• <b>直式公式</b>：<code style='font-size:13px; color:#b91c1c; font-weight:bold;'>空間占比(%) = (單線實際截面積 × 載流導線數) / (線槽寬 × 線槽高) × 100%</code><br>"
                f"&nbsp;&nbsp;• <b>參數帶入</b>：導線總截面 (單線 {single_wa} mm² × {w_cnt_int} 根 = {twa:.2f} mm²) / 線槽面積 ({w_tray} × {h_tray} = {tray_area} mm²)<br>"
                f"&nbsp;&nbsp;• <b>法規協調</b>：線槽空間占比 ({rt_d}%) ≤ 法規極限 (20.0%) ➜ <span style='font-weight:bold; color:{'#16a34a' if 'OK' in rst_d else '#dc2626'}'>{rst_d}</span>"
            )
        except Exception:
            tray_html = "&nbsp;&nbsp;• <b>法規協調</b>：線槽格式解析失敗，請確認格式 (如 100x50)。"
    else:
        tray_html = "&nbsp;&nbsp;• <b>法規協調</b>：未選擇線槽或無效導線，免計空間占比。"

    # 七、 接地系統檢討
    is_main_ground = (cir == '進屋線/變壓器二次側')
    if is_main_ground:
        try: w_val = float(wire)
        except: w_val = 0.0
        req_solid = 0.0
        if w_val <= 14: req_strand = 8.0
        elif w_val <= 38: req_strand = 14.0
        elif w_val <= 100: req_strand = 22.0
        elif w_val <= 250: req_strand = 38.0
        elif w_val <= 500: req_strand = 50.0
        else: req_strand = 60.0
        ground_table_name = "【表二六之一】(內線系統單獨接地-依最大導線)"
        param_desc = f"進屋線/相導線線徑 {wire} mm²"
    else:
        if nfb <= 20: req_solid, req_strand = 1.6, 2.0
        elif nfb <= 30: req_solid, req_strand = 2.0, 3.5
        elif nfb <= 60: req_solid, req_strand = 0.0, 5.5
        elif nfb <= 100: req_solid, req_strand = 0.0, 8.0
        elif nfb <= 200: req_solid, req_strand = 0.0, 14.0
        elif nfb <= 400: req_solid, req_strand = 0.0, 22.0
        elif nfb <= 600: req_solid, req_strand = 0.0, 38.0
        else: req_solid, req_strand = 0.0, 38.0
        ground_table_name = "【表二六之二】(設備接地-依NFB額定)"
        param_desc = f"當前 NFB 額定 {nfb}A"
    
    gw_val = get_num(gw)
    gw_unit = 'mm' if gw in ['1.6', '2.0'] else 'mm²'
    req_unit = 'mm (單線)' if req_solid > 0 else 'mm² (絞線)'
    req_val = req_solid if req_solid > 0 else req_strand
    
    if gw in ['1.6', '2.0']: gst = "✅ OK" if (req_solid > 0 and gw_val >= req_solid) else "❌ NG"
    else: gst = "✅ OK" if gw_val >= req_strand else "❌ NG"
        
    gw_html = (
        f"&nbsp;&nbsp;• <b>查表依據</b>：{ground_table_name}<br>"
        f"&nbsp;&nbsp;• <b>參數帶入</b>：{param_desc} ➜ 法規最小需求為 {req_val} {req_unit}<br>"
        f"&nbsp;&nbsp;• <b>法規協調</b>：設計接地線徑 ({gw_val} {gw_unit}) ≥ 最小需求 ({req_val} {gw_unit}) ➜ <span style='font-weight:bold; color:{'#16a34a' if 'OK' in gst else '#dc2626'}'>{gst}</span>"
    )

    vol_g = round(vol / 1.73205, 1) if '三相' in ph else vol
    r_lim = 10.0 if (is_high_voltage or '第一種' in g_type or '特種' in g_type) else (50.0 if vol_g <= 300 else 10.0)
    grst = "✅ OK" if gr <= r_lim else "❌ NG"
    
    gr_html = (
        f"&nbsp;&nbsp;• <b>查表依據</b>：【表二五】(各接地種類電阻限制)<br>"
        f"&nbsp;&nbsp;• <b>參數帶入</b>：對地電壓 {vol_g}V / {g_type} ➜ 法規極限值為 {r_lim} Ω<br>"
        f"&nbsp;&nbsp;• <b>法規協調</b>：實測/設計電阻 ({gr} Ω) ≤ 法規極限值 ({r_lim} Ω) ➜ <span style='font-weight:bold; color:{'#16a34a' if 'OK' in grst else '#dc2626'}'>{grst}</span>"
    )
    z_base_print = ((vol/1000.0)**2) / (base_kva/1000) if base_kva > 0 else 0.0

    # 八、 線損率計算
    if wire_type == '無' or wire == '無':
        p_loss_w, loss_pct, k_loss, r_line = 0.0, 0.0, 0, 0.0
    else:
        r_line, x_line = get_rx_values(wire.strip(), wire_type, ins)
        k_loss = 3.0 if '三相' in ph else 2.0
        p_loss_w = round(k_loss * (calc_c**2) * r_line * (length / 1000.0), 2)
        loss_pct = round((p_loss_w / (kw * 1000)) * 100, 3) if kw > 0 else 0.0

    html_loss_block = f"""
    <div style="margin-top: 15px; background: #1e293b; color: #10b981; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 13px; border: 1px solid #0f172a; line-height: 1.7;">
        <div style="color: #cbd5e1; margin-bottom: 8px; font-weight: bold; font-size: 14px; font-family: 'Segoe UI', Arial, sans-serif;">八、 線損率直式計算表 (法規依據：進屋線 / 變壓器二次側檢討)</div>
        &nbsp;&nbsp;• <b>直式公式</b>：<code style="font-size:13px; color:#f43f5e; font-weight:bold;">P_loss(W) = K × I² × R_ac × (L/1000), 線損率(%) = P_loss / (kW × 1000) × 100%</code><br>
        &nbsp;&nbsp;• <span style="color:#94a3b8;">實體阻抗 R_ac</span> = {r_line} Ω/km<br>
        &nbsp;&nbsp;• <span style="color:#94a3b8;">常數 K</span> = {int(k_loss)} ({"三相" if "三相" in ph else "單相"})<br>
        &nbsp;&nbsp;• <span style="color:#94a3b8;">P_loss (W)</span> = {int(k_loss)} × ({calc_c})² × {r_line} × ({length}/1000) = <b>{p_loss_w} W</b><br>
        &nbsp;&nbsp;• <span style="color:#94a3b8;">Loss (%)</span> = ({p_loss_w} / {kw*1000 if kw > 0 else 0.0}) × 100% = <b>{loss_pct} %</b>
    </div>
    """ if is_main_ground else """
    <div style="margin-top: 15px; background: #f8fafc; color: #64748b; padding: 12px 15px; border-radius: 8px; font-size: 12px; border: 1px solid #e2e8f0;">
        <b>八、 線損率直式計算表</b> ➜ ➖ 當前為幹線/分路迴路，免計錶前至責分點線損。（切換至「受電盤/錶箱」時自動啟動直式計算）
    </div>
    """

    html_out = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; border: 2px solid #1e3a8a; border-radius: 10px; overflow: hidden; width: 100%; background: #ffffff; margin-top: 15px;">
        <div style="background: #1e3a8a; color: #ffffff; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; font-size: 16px; font-weight: 600;">📊 單線圖直式公式審查報告 ➜ 【 {cir_id_name} 】</h3>
            <span style="font-size: 12px; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 4px; font-weight: bold;">八大章節 / 網頁升級版</span>
        </div>
        <div style="padding: 20px; line-height: 1.6; font-size: 13px; color: #334155;">
            
            <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #cbd5e1;">
                <b style="font-size: 14px; color: #1e3a8a;">一、 負載運算與基準電流 (法規依據：實務電學原理)</b><br>
                &nbsp;&nbsp;• <b>直式公式</b>：<code style="font-size:13px; color:#b91c1c; font-weight:bold;">{formula_text}</code><br>
                &nbsp;&nbsp;• <b>數值代入</b>：<code style="font-size:13px; color:#0f766e; font-weight:bold;">{substitution_text}</code>
            </div>

            <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #cbd5e1;">
                <b style="font-size: 14px; color: #1e3a8a;">二、 斷路器與導線安培容量協調 (法規依據：《裝置規則》第 16、53 條)</b><br>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; margin-top: 5px; font-size: 12px; border: 1px solid #e2e8f0; line-height: 1.7;">
                    <b>【保護開關檢討】</b><br>
                    &nbsp;&nbsp;• <b>法規協調</b>：過電流保護裝置額定 (NFB: {nfb}A) ≥ 負載計算電流 ({calc_c}A) ➜ <span style="font-weight:bold; color:{'#16a34a' if 'OK' in nst else '#dc2626'}">{nst}</span><br><br>
                    <b>【導線容量檢討】</b><br>
                    {wire_html_detail}
                </div>
            </div>

            <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #cbd5e1;">
                <b style="font-size: 14px; color: #1e3a8a;">三、 線路電壓降級聯計算 (法規依據：《裝置規則》第 9 條)</b><br>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; margin-top: 5px; font-size: 12px; border: 1px solid #e2e8f0; line-height: 1.7;">
                    {vd_html_detail}
                </div>
            </div>

            <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #cbd5e1;">
                <b style="font-size: 14px; color: #1e3a8a;">四、 法定最低 ICU 啟斷容量對照檢討 (法規依據：《裝置規則》第 58 條附表)</b><br>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; margin-top: 5px; font-size: 12px; border: 1px solid #e2e8f0; line-height: 1.7;">
                    {ic_html_detail}
                </div>
            </div>

            <div style="margin-bottom: 15px; padding-bottom: 15px; background: #fdfaf0; padding: 15px; border-radius: 8px; border: 1px solid #fbcfe8;">
                <b style="font-size: 14px; color: #9d174d;">五、 系統級聯故障電流與換底公式 (法規依據：《裝置規則》第 58 條消弧比對)</b><br>
                <div style="margin-top: 8px; font-size: 12px; color: #1e293b; line-height: 1.7;">
                    <b>【Step 1: 建立系統標么基準值 (Per-Unit Base)】</b><br>
                    &nbsp;&nbsp;• S_base = <span style="color:#2563eb; font-weight:bold;">{base_kva} kVA ({base_kva/1000} MVA)</span> | V_base = <span style="color:#2563eb; font-weight:bold;">{vol/1000:.3f} kV</span><br>
                    &nbsp;&nbsp;• I_base = S_base / ({"√3 × " if "三相" in ph else ""}{vol/1000:.3f}kV) = <b>{i_base:.2f} A</b><br>
                    &nbsp;&nbsp;• Z_base = (V_base)² × 1000 / S_base = <b>{z_base_print:.5f} Ω (pu化分母)</b><br><br>
                    <b>【Step 2: 阻抗向量逐段級聯相加 (ΣZ_pu = ΣR + jΣX)】</b><br>
                    {sc_cascade_html}
                    &nbsp;&nbsp;• <b>總向量合成阻抗：</b> ΣZ_total = <b>{z_total.real:.5f} + j{z_total.imag:.5f} pu</b> (絕對值 |Z| = <span style="color:#b91c1c; font-weight:bold;">{z_mag:.5f}</span>)<br><br>
                    <b>【Step 3: 短路開關啟斷容量 (IC) 衝擊驗證】</b><br>
                    &nbsp;&nbsp;• 對稱短路電流 I_sym = I_base / (|Z| × 1000) = <b>{i_sym:.2f} kA</b><br>
                    &nbsp;&nbsp;• 非對稱短路電流 I_asym = I_sym × K({k_factor}) = <span style="color:#ea580c; font-weight:bold;">{i_asym:.2f} kA</span><br>
                    &nbsp;&nbsp;• <b>法規協調：</b> 設備開關 IC ({ic_ka} kA) ≥ 系統最大衝擊電流 ({i_asym:.2f} kA) ➜ <span style="font-weight:bold; color:{'#16a34a' if fc_ok else '#dc2626'}">{fc_st}</span>
                </div>
            </div>

            <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #cbd5e1;">
                <b style="font-size: 14px; color: #1e3a8a;">六、 匯流排與線槽空間占比檢討 (法規依據：《裝置規則》第 16、252 條)</b><br>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; margin-top: 5px; font-size: 12px; border: 1px solid #e2e8f0; line-height: 1.7;">
                    <b>【匯流排容量檢討】</b><br>{busway_html}<br><br>
                    <b>【線槽占比檢討】</b><br>{tray_html}
                </div>
            </div>

            <div style="margin-bottom: 15px; padding-bottom: 15px;">
                <b style="font-size: 14px; color: #1e3a8a;">七、 接地系統配置檢討 (法規依據：《裝置規則》第 24、25、26 條)</b><br>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; margin-top: 5px; font-size: 12px; border: 1px solid #e2e8f0; line-height: 1.7;">
                    <b>【接地線徑檢討】</b><br>{gw_html}<br><br>
                    <b>【接地電阻檢討】</b><br>{gr_html}
                </div>
            </div>

            {html_loss_block}

        </div>
    </div>
    """
    return html_out

# ==========================================
# 3. Streamlit 介面狀態管理與初始化
# ==========================================
CIRCUIT_LIST = [
    '1. 受電盤 (Main)', '2. 用户錶箱 (Meter)', '3. MP總配電盤 (Main)',
    '4. MP盤下游-幹線01', '5. MP盤下游-幹線02', '6. MP盤下游-幹線03', '7. MP盤下游-幹線04', '8. MP盤下游-幹線05',
    '9. MP盤下游-幹線06', '10. MP盤下游-幹線07', '11. MP盤下游-幹線08', '12. MP盤下游-幹線09', '13. MP盤下游-幹線10',
    '14. 幹線01下游-次幹線01', '15. 幹線02下游-次幹線02', '16. 幹線03下游-次幹線03', '17. 幹線04下游-次幹線04', '18. 幹線05下游-次幹線05',
    '19. 幹線06下游-次幹線06', '20. 幹線07下游-次幹線07', '21. 幹線08下游-次幹線08', '22. 幹線09下游-次幹線09', '23. 幹線10下游-次幹線10',
    '24. APFC功因補償電容 01', '25. APFC功因補償電容 02', '26. APFC功因補償電容 03', '27. APFC功因補償電容 04', '28. APFC功因補償電容 05'
]

if 'circuit_db' not in st.session_state:
    db = {}
    for c in CIRCUIT_LIST:
        is_cap = ('電容' in c)
        is_subtrunk = ('次幹線' in c)
        is_trunk = ('幹線' in c and not is_subtrunk)
        if '受電盤' in c: up_source = '無'
        elif '錶箱' in c: up_source = '1. 受電盤 (Main)'
        elif 'MP總' in c: up_source = '2. 用户錶箱 (Meter)'
        elif is_trunk or is_cap: up_source = '3. MP總配電盤 (Main)'
        elif is_subtrunk:
            idx_str = c.split('次幹線')[1] if '次幹線' in c else '01'
            matching_trunk = '3. MP總配電盤 (Main)'
            for trunk in CIRCUIT_LIST:
                if f'幹線{idx_str}' in trunk and '下游' in trunk and '次幹線' not in trunk:
                    matching_trunk = trunk
                    break
            up_source = matching_trunk
        else: up_source = '無'
        
        db[c] = {
            'ph': '無', 'kw': 0.0, 'vol': '無', 'pf': 0.85, 'length': 0.0, 'up': up_source,
            'nfb': '無', 'ins': '無', 'wire_type': '無', 'wire': '無', 'cnt': 0, 'pipe_opt': '無', 'busway': '無',
            'ds': '無', 'gtype': '無', 'gw': '無', 'gr': 0.0, 'ic': 0.0, 'loc': '無', 'kvar': 0.0,
            'base_kva': 1000.0, 'k_factor': 1.01, 'tpc_vol': '無', 'tpc_mva': 0.0,
            'tx_kva': 0.0, 'tx_pct_r': 0.0, 'tx_pct_x': 0.0
        }
    st.session_state.circuit_db = db

# ==========================================
# 4. 前端側邊欄 UI 渲染與資料綁定
# ==========================================
st.sidebar.title("參數輸入控制台")
cur_node = st.sidebar.selectbox("⚡ 選擇當前查核節點:", CIRCUIT_LIST)

cd = st.session_state.circuit_db[cur_node]
is_entrance = ('受電盤' in cur_node)

with st.sidebar.expander("1. 系統負載與架構", expanded=True):
    new_ph = st.selectbox("相線:", ['無', '三相三', '三相四', '單相三', '單相二'], index=['無', '三相三', '三相四', '單相三', '單相二'].index(cd['ph']) if cd['ph'] in ['無', '三相三', '三相四', '單相三', '單相二'] else 0)
    new_vol = st.selectbox("電壓(V):", ['無', '110', '220', '380', '440', '11400', '22800'], index=['無', '110', '220', '380', '440', '11400', '22800'].index(cd['vol']) if cd['vol'] in ['無', '110', '220', '380', '440', '11400', '22800'] else 0)
    new_kw = st.number_input("實功率 (kW):", value=float(cd['kw']), min_value=0.0, step=1.0)
    new_pf = st.number_input("功率因數 (PF):", value=float(cd['pf']), min_value=0.0, max_value=1.0, step=0.01)
    
    st.info(f"💡 馬力(HP): {round(new_kw/0.746, 2)} | 視在(kVA): {round(new_kw/new_pf, 2) if new_pf>0 else 0}")
    
    new_up = st.selectbox("上游來源:", ['無'] + CIRCUIT_LIST, index=(['無'] + CIRCUIT_LIST).index(cd['up']) if cd['up'] in (['無'] + CIRCUIT_LIST) else 0)
    new_len = st.number_input("線路長度 (m):", value=float(cd['length']), min_value=0.0, step=1.0)

with st.sidebar.expander("2. 斷路器與保護配置", expanded=False):
    ALL_NFB = ['無', '15', '20', '30', '40', '50', '60', '75', '100', '125', '150', '175', '200', '225', '250', '300', '400', '500', '600', '800', '1000', '1200']
    new_nfb = st.selectbox("NFB (AT):", ALL_NFB, index=ALL_NFB.index(str(cd['nfb'])) if str(cd['nfb']) in ALL_NFB else 0)
    new_ic = st.number_input("IC (kA):", value=float(cd['ic']), min_value=0.0, step=5.0)
    new_loc = st.selectbox("安裝位置:", ['無', '受電箱', '集中(單獨)表箱', '用戶總開關箱'], index=['無', '受電箱', '集中(單獨)表箱', '用戶總開關箱'].index(cd['loc']) if cd['loc'] in ['無', '受電箱', '集中(單獨)表箱', '用戶總開關箱'] else 0)

with st.sidebar.expander("3. 導線安培容量配置", expanded=False):
    new_ins = st.selectbox("絕緣材質:", ['無', 'PVC(60℃)', 'XLPE(90℃)'], index=['無', 'PVC(60℃)', 'XLPE(90℃)'].index(cd['ins']) if cd['ins'] in ['無', 'PVC(60℃)', 'XLPE(90℃)'] else 0)
    new_wtype = st.selectbox("導線類型:", ['無', '單芯線', '絞線'], index=['無', '單芯線', '絞線'].index(cd['wire_type']) if cd['wire_type'] in ['無', '單芯線', '絞線'] else 0)
    ALL_WIRE = ['無', '1.6', '2.0', '2.6', '3.5', '5.5', '8', '14', '22', '30', '38', '50', '60', '80', '100', '125', '150', '200', '250', '325', '400', '500']
    new_wire = st.selectbox("線徑:", ALL_WIRE, index=ALL_WIRE.index(str(cd['wire'])) if str(cd['wire']) in ALL_WIRE else 0)
    new_cnt = st.number_input("載流導線數:", value=int(cd['cnt']), min_value=0, step=1)
    new_pipe = st.selectbox("配管選項:", ['無', '金屬管', 'PVC管'], index=['無', '金屬管', 'PVC管'].index(cd['pipe_opt']) if cd['pipe_opt'] in ['無', '金屬管', 'PVC管'] else 0)

with st.sidebar.expander("4. 接地系統與匯流排/線槽", expanded=False):
    new_gtype = st.selectbox("接地種類:", ['無', '特種接地', '第一種接地', '第二種接地', '第三種接地'], index=['無', '特種接地', '第一種接地', '第二種接地', '第三種接地'].index(cd['gtype']) if cd['gtype'] in ['無', '特種接地', '第一種接地', '第二種接地', '第三種接地'] else 0)
    new_gw = st.selectbox("接地線徑:", ALL_WIRE, index=ALL_WIRE.index(str(cd['gw'])) if str(cd['gw']) in ALL_WIRE else 0)
    new_gr = st.number_input("實測電阻 (Ω):", value=float(cd['gr']), min_value=0.0, step=1.0)
    new_busway = st.selectbox("匯流排規格:", ['無'] + list(BUSWAY_DB.keys()), index=(['無'] + list(BUSWAY_DB.keys())).index(cd['busway']) if cd['busway'] in (['無'] + list(BUSWAY_DB.keys())) else 0)
    new_ds = st.selectbox("線槽:", ['無', '50x50', '100x50', '100x100', '200x100', '300x100', '400x100'], index=['無', '50x50', '100x50', '100x100', '200x100', '300x100', '400x100'].index(cd['ds']) if cd['ds'] in ['無', '50x50', '100x50', '100x100', '200x100', '300x100', '400x100'] else 0)

with st.sidebar.expander("5. 短路電流 TPC端設定 (僅受電盤可改)", expanded=is_entrance):
    main_db = st.session_state.circuit_db['1. 受電盤 (Main)']
    new_tpc_vol = st.selectbox("台電電壓:", ['無', '11.4 kV', '22.8 kV'], index=['無', '11.4 kV', '22.8 kV'].index(main_db['tpc_vol']) if main_db['tpc_vol'] in ['無', '11.4 kV', '22.8 kV'] else 0, disabled=not is_entrance)
    auto_mva = 0.0 if new_tpc_vol == '無' else (250.0 if "11.4" in new_tpc_vol else 500.0)
    st.info(f"短路容量: {auto_mva} MVA")
    
    new_tx_kva = st.number_input("變壓器 KVA:", value=float(main_db['tx_kva']), min_value=0.0, step=50.0, disabled=not is_entrance)
    auto_r, auto_x = main_db['tx_pct_r'], main_db['tx_pct_x']
    if new_tx_kva > 0 and is_entrance:
        closest_kva = min(TX_IMPEDANCE_DB.keys(), key=lambda k: abs(k - new_tx_kva))
        auto_r, auto_x = TX_IMPEDANCE_DB[closest_kva]
    
    col1, col2 = st.columns(2)
    with col1: new_tx_r = st.number_input("% R:", value=float(auto_r), step=0.1, disabled=not is_entrance)
    with col2: new_tx_x = st.number_input("% X:", value=float(auto_x), step=0.1, disabled=not is_entrance)
    
    new_base = st.number_input("系統基準 kVA:", value=float(main_db['base_kva']), step=100.0, disabled=not is_entrance)
    new_kf = st.number_input("K 係數 (非對稱):", value=float(main_db['k_factor']), step=0.01, disabled=not is_entrance)

# 寫入狀態庫
cd.update({
    'ph': new_ph, 'kw': new_kw, 'vol': new_vol, 'pf': new_pf, 'up': new_up, 'length': new_len,
    'nfb': new_nfb, 'ic': new_ic, 'loc': new_loc, 'ins': new_ins, 'wire_type': new_wtype,
    'wire': new_wire, 'cnt': new_cnt, 'pipe_opt': new_pipe, 'gtype': new_gtype, 'gw': new_gw,
    'gr': new_gr, 'busway': new_busway, 'ds': new_ds
})

if is_entrance:
    cd.update({'tpc_vol': new_tpc_vol, 'tpc_mva': auto_mva, 'tx_kva': new_tx_kva, 'tx_pct_r': new_tx_r, 'tx_pct_x': new_tx_x, 'base_kva': new_base, 'k_factor': new_kf})
else:
    for k in ['tpc_vol', 'tpc_mva', 'tx_kva', 'tx_pct_r', 'tx_pct_x', 'base_kva', 'k_factor']:
        cd[k] = main_db[k]

# ==========================================
# 5. 主畫面執行與渲染 HTML
# ==========================================
import re
st.title("🖥️ 電氣系統查核引擎")
final_html = design_ai(cd, cur_node, st.session_state.circuit_db)

# 施展除錯魔法：把因為排版產生的小空格全部清掉，避免 Streamlit 誤判為純文字
clean_html = re.sub(r'\n\s+', '\n', final_html)
st.markdown(clean_html, unsafe_allow_html=True)