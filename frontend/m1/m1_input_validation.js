const URL_STEP1 = "http://127.0.0.1:8000/api/v1/calculate/motor";
const URL_STEP34 = "http://127.0.0.1:8000/api/v1/calculate/motor/step3_4";

let state = {
    pt: null, 
    niv: null, 
    motors: [], 
    selectedMotor: null
};

function showToast(type, msg) {
  const wrap = document.getElementById('toastWrap');
  if(!wrap) return;
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  const icons = { ok:'✅', error:'❌', warn:'⚠️' };
  t.innerHTML = `<span class="toast-icon">${icons[type]||'ℹ️'}</span><span class="toast-msg">${msg}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
  wrap.appendChild(t);
  setTimeout(() => { 
    t.style.opacity='0'; t.style.transform='translateX(20px)'; 
    t.style.transition='all 0.3s'; 
    setTimeout(()=>t.remove(), 300); 
  }, 4500);
}

// XỬ LÝ ĐẦU VÀO & TÍNH SƠ BỘ 
window.runStep1 = async function() {
    const inputPt = document.getElementById("inputPt");
    const inputNiv = document.getElementById("inputNiv");
    if (!inputPt || !inputNiv) return;

    const pt = parseFloat(inputPt.value);
    const niv = parseFloat(inputNiv.value);
    
    if(!pt || !niv) {
        showToast('error', 'Vui lòng nhập công suất và vòng quay hợp lý!');
        return;
    }
    
    if (pt <= 0 || pt > 100) {
        showToast('error', 'Công suất Pt phải lớn hơn 0 và nhỏ hơn 100 kW');
        return;
    }
    
    state.pt = pt; 
    state.niv = niv;
    
    // Gửi payload lên API 1
    const payload = { p_tai_w: pt * 1000, n_lv: niv, he_so_tai: 1.0 };
    
    try {
        const res = await fetch(URL_STEP1, {
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) throw new Error("API call failed");
        
        const json = await res.json();
        const data = json.data;
        
        // Lưu trữ P_ct vào state để dùng cho các bước tính sau
        state.pct = data.muc_2_1_2.p_ct;
        
        // 1. Hiển thị kết quả trung gian
        document.getElementById("step1-results").style.display = "block";
        document.getElementById("outPct").textContent = data.muc_2_1_2.p_ct.toFixed(2) + " kW";
        document.getElementById("outNsb").textContent = data.muc_2_1_3.n_sb.toFixed(2) + " v/ph";
        
        // 2. Render danh sách Động cơ (Bước 2)
        state.motors = data.muc_2_1_4_goi_y || [];
        renderMotors(data.muc_2_1_3.n_sb);
        document.getElementById("step2").classList.add("active");
        
        showToast('ok', 'Đã tính toán sơ bộ thành công!');
        
    } catch(e) { 
        console.error(e);
        showToast('error', 'Lỗi Backend: Hãy chắc chắn Server Python đang chạy!'); 
    }
};

// ── BƯỚC 2: RENDER BẢNG CHỌN ĐỘNG CƠ ──
function renderMotors(nsb) {
    const tbody = document.getElementById("motorTableBody");
    tbody.innerHTML = '';
    
    if(state.motors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--tx2);">Không tìm thấy động cơ phù hợp</td></tr>';
        return;
    }
    
    state.motors.forEach((m, idx) => {
        const diff = Math.abs(m.n - nsb);
        let badge = '';
        if (idx === 0) {
            badge = '<span class="badge-rec">Khuyên dùng</span>';
        }
        
        tbody.innerHTML += `
            <tr>
                <td><strong>${m.code}</strong> ${badge}</td>
                <td><span style="font-family:var(--mono)">${m.P.toFixed(2)}</span></td>
                <td><span style="font-family:var(--mono)">${m.n.toFixed(0)}</span></td>
                <td><span style="font-family:var(--mono)">${(m.tk_tdn || 0).toFixed(1)}</span></td>
                <td style="color:var(--tx2);">±<span style="font-family:var(--mono)">${diff.toFixed(1)}</span></td>
                <td style="text-align:right;"><button class="btn-select" id="btnSel_${idx}" onclick="selectMotor(${idx})">Chọn động cơ</button></td>
            </tr>
        `;
    });
}

// ── BƯỚC 2.5: XỬ LÝ CHỌN ĐỘNG CƠ MỚI ──
window.selectMotor = async function(idx) {
    state.selectedMotor = state.motors[idx];
    
    // Đổi hiển thị màu nút bấm
    document.querySelectorAll('.btn-select').forEach(b => { 
        b.style.background = 'transparent'; 
        b.style.color = 'var(--blue)'; 
        b.textContent = 'Chọn động cơ'; 
    });
    const btn = document.getElementById(`btnSel_${idx}`);
    if(btn) {
        btn.style.background = 'var(--blue)'; 
        btn.style.color = '#fff'; 
        btn.textContent = 'Đã chọn ✓';
    }
    
    // Mở khóa UI Bước 3
    document.getElementById("step3").classList.add("active");
    
    // Mở khóa luôn UI Bước 4
    document.getElementById("step4").classList.add("active");
    
    // Tiến hành nạp dữ liệu từ Backend Step 3_4
    await fetchStep34();
};

// ── BƯỚC 3 & 4: LẤY DỮ LIỆU KIỂM NGHIỆM VÀ ĐỘNG LỰC HỌC ──
async function fetchStep34() {
    if(!state.selectedMotor) return;
    const kqt = parseFloat(document.getElementById("inputKqt").value) || 1.3;
    
    // Tạo bản sao của động cơ được chọn nhưng ghi đè P thành P_ct
    const customMotor = { ...state.selectedMotor, P: state.pct || state.selectedMotor.P };
    
    const payload = {
        motor: customMotor,
        k_qt: kqt,
        n_iv: state.niv
    };
    
    try {
        const res = await fetch(URL_STEP34, {
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) throw new Error("API call failed");
        
        const json = await res.json();
        const validation = json.validation;
        const kin = json.kinematics;
        const ratios = json.ratios;
        
        // ── XỬ LÝ BƯỚC 3: HIỂN THỊ ĐÈN TRẠNG THÁI KIỂM NGHIỆM ──
        const light = document.getElementById("valLight");
        const title = document.getElementById("valTitle");
        const desc = document.getElementById("valDesc");
        
        if(validation.is_valid) {
            light.className = "light-indicator light-green";
            title.textContent = "Đạt yêu cầu"; 
            title.style.color = "var(--green)";
            desc.innerHTML = `Hệ số đáp ứng: ${validation.message}`;
        } else {
            light.className = "light-indicator light-red";
            title.textContent = "Không đạt yêu cầu (Failed)"; 
            title.style.color = "var(--red)";
            desc.innerHTML = `Vui lòng chọn động cơ có mô-men khởi động <strong>Tk/Tdn lớn hơn</strong> hoặc tăng công suất. <br><em style="color:#d9534f">${val.message}</em>`;
        }
        
        // ── XỬ LÝ BƯỚC 4: RENDER BẢNG MA TRẬN ĐỘNG LỰC HỌC ──
        if(kin && ratios) {
            // Định dạng theo quy tắc làm tròn tiêu chuẩn
            const format_P = (v) => v ? parseFloat(v).toFixed(3) : '-'; // P: 3 chữ số thập phân
            const format_n = (v) => v ? parseFloat(v).toFixed(1) : '-'; // n: 1 chữ số thập phân
            const format_T = (v) => v ? parseFloat(v).toFixed(3) : '-'; // T: 3 chữ số thập phân
            const format_u = (v) => v ? parseFloat(v).toFixed(4) : '-'; // u: 4 chữ số thập phân
            
            // Hàm lấy an toàn
            const getVal = (key, prop) => kin[key] && kin[key][prop] !== undefined ? kin[key][prop] : null;
            
            // Cột: Động cơ
            document.getElementById("t_P_dc").textContent = format_P(getVal('truc_dc', 'P'));
            document.getElementById("t_n_dc").textContent = getVal('truc_dc', 'n') ? Math.round(val('truc_dc', 'n')) : '-'; // n_dc lấy nguyên
            document.getElementById("t_T_dc").textContent = format_T(getVal('truc_dc', 'T'));
            document.getElementById("t_u_dc").textContent = '-';
            
            // Cột: Trục I
            document.getElementById("t_P_1").textContent = format_P(getVal('truc_1', 'P'));
            document.getElementById("t_n_1").textContent = format_n(getVal('truc_1', 'n'));
            document.getElementById("t_T_1").textContent = format_T(getVal('truc_1', 'T'));
            document.getElementById("t_u_1").textContent = format_u(ratios.u_dai);
            
            // Cột: Trục II
            document.getElementById("t_P_2").textContent = format_P(getVal('truc_2', 'P'));
            document.getElementById("t_n_2").textContent = format_n(getVal('truc_2', 'n'));
            document.getElementById("t_T_2").textContent = format_T(getVal('truc_2', 'T'));
            document.getElementById("t_u_2").textContent = format_u(ratios.u_1);
            
            // Cột: Trục III
            document.getElementById("t_P_3").textContent = format_P(getVal('truc_3', 'P'));
            document.getElementById("t_n_3").textContent = format_n(getVal('truc_3', 'n'));
            document.getElementById("t_T_3").textContent = format_T(getVal('truc_3', 'T'));
            document.getElementById("t_u_3").textContent = format_u(ratios.u_2);
            
            // Vẽ biểu đồ Moment
            renderTorqueChart(kin);

            // ───── SAVE DATA FOR M2 ─────
            saveModuleData(STORAGE_KEYS.M1, {
                input: {
                    pt: state.pt,
                    niv: state.niv
                },

                motor: state.selectedMotor,

                power: {
                    pct: state.pct
                },

                ratios: ratios,

                kinematics: kin,

                validation: validation,

                timestamp: new Date().toISOString()
            });
        }
    } catch(e) { 
        console.error(e);
        showToast('error', 'Lỗi khi tải bảng Động lực học!'); 
    }
}

function renderTorqueChart(kin) {
    const chart = document.getElementById("chartMoment");
    if(!chart || !kin) return;
    
    const T_dc = parseFloat(kin.truc_dc?.T || 0);
    const T_1 = parseFloat(kin.truc_1?.T || 0);
    const T_2 = parseFloat(kin.truc_2?.T || 0);
    const T_3 = parseFloat(kin.truc_3?.T || 0);
    
    // Tìm max để chia tỉ lệ phần trăm (Thường T_3 lớn nhất)
    const maxT = Math.max(T_dc, T_1, T_2, T_3);
    if(maxT === 0) return;
    
    const bars = [
        { label: 'Động cơ', val: T_dc, color: 'var(--tx3)' },
        { label: 'Trục I', val: T_1, color: 'var(--blue)' },
        { label: 'Trục II', val: T_2, color: 'var(--teal)' },
        { label: 'Trục III', val: T_3, color: 'var(--violet)' }
    ];
    
    chart.innerHTML = '';
    // Thêm hiệu ứng trễ một xíu cho animation
    setTimeout(() => {
        bars.forEach(b => {
            const pct = (b.val / maxT) * 100;
            // Dùng template literals với style inline để vẽ thanh bar
            chart.innerHTML += `
                <div style="display:flex; align-items:center; font-size:13px; font-weight:500;">
                    <div style="width: 100px; color:var(--tx2);">${b.label}</div>
                    <div style="flex:1; background:var(--bg3); height:22px; border-radius:6px; overflow:hidden; position:relative; box-shadow:inset 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="height:100%; width:0%; background:${b.color}; transition: width 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.1s; border-radius:6px;" data-width="${pct}%"></div>
                    </div>
                    <div style="width: 110px; text-align:right; font-family:var(--mono); color:var(--tx1); font-weight:700;">
                        ${b.val.toLocaleString('en-US', {maximumFractionDigits:0})} <span style="font-size:10px;color:var(--tx3);font-weight:400;">N.mm</span>
                    </div>
                </div>
            `;
        });
        
        // Kích hoạt animation
        setTimeout(() => {
            chart.querySelectorAll('[data-width]').forEach(el => {
                el.style.width = el.getAttribute('data-width');
            });
        }, 50);
    }, 100);
}

// Bắt sự kiện khi user sửa Kqt (Bước 3) -> tự rẽ nhánh tính lại
window.reValidate = function() {
    if(!state.selectedMotor) return;
    fetchStep34();
};

window.addEventListener(
    "DOMContentLoaded",
    restoreM1State
);

function restoreM1State() {

    const saved =
        loadModuleData(STORAGE_KEYS.M1);

    if(!saved) return;

    // Restore input
    restoreInput(
        "inputPt",
        saved.input.pt
    );

    restoreInput(
        "inputNiv",
        saved.input.niv
    );

    // Restore state
    state.pt = saved.input.pt;

    state.niv = saved.input.niv;

    state.selectedMotor =
        saved.motor;

    state.pct =
        saved.power.pct;

    // Nếu muốn auto render lại
    if(saved.kinematics) {

        document
            .getElementById("step2")
            .classList.add("active");

        document
            .getElementById("step3")
            .classList.add("active");

        document
            .getElementById("step4")
            .classList.add("active");
    }

    showToast(
        'ok',
        'Đã khôi phục dữ liệu M1'
    );
}